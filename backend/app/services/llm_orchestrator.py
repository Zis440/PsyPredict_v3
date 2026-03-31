"""
llm_orchestrator.py — Intelligent Dual-LLM Routing Engine for PsyPredict

Manages both local (Ollama) and cloud (Groq) LLM clients simultaneously.
Routes requests based on:
  - Task type (routine chat, long-form summary, knowledge retrieval)
  - Privacy sensitivity (PII detected → local only)
  - Provider availability (automatic fallback)
  - Latency requirements

Features:
  - Automatic fallback: if primary fails, retries on secondary
  - PII scrubbing before cloud calls
  - Per-request routing metadata logging
  - Periodic health checks for both providers
  - Cost/latency tracking per provider
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Dict, List, Optional

from app.config import get_settings
from app.schemas import ConversationMessage, PsychReport, fallback_report
from app.services.base_llm_client import BaseLLMClient
from app.services.pii_scrubber import PIIScrubber, ScrubResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums & Data Classes
# ---------------------------------------------------------------------------

class TaskType(str, Enum):
    """Types of LLM tasks with different routing priorities."""
    ROUTINE_CHAT = "routine_chat"            # Normal conversational turn
    LONG_FORM_SUMMARY = "long_form_summary"  # Progress summary, deep reflection
    PROGRESS_ANALYSIS = "progress_analysis"  # Analyzing patient trends
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"  # Complex medical query


class ProviderPreference(str, Enum):
    """Which provider to prefer for a given task."""
    LOCAL = "local"     # Ollama — low latency, privacy-first
    CLOUD = "cloud"     # Groq — high throughput, large context
    AUTO = "auto"       # Let orchestrator decide


@dataclass
class RoutingDecision:
    """Metadata about how a request was routed."""
    provider_used: str          # "ollama" or "groq"
    task_type: str
    latency_ms: float
    fallback_used: bool = False
    fallback_provider: Optional[str] = None
    pii_scrubbed: bool = False
    pii_types: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class OrchestratorStats:
    """Aggregate stats for monitoring."""
    total_requests: int = 0
    local_requests: int = 0
    cloud_requests: int = 0
    fallback_count: int = 0
    pii_scrub_count: int = 0
    avg_local_latency_ms: float = 0.0
    avg_cloud_latency_ms: float = 0.0
    local_errors: int = 0
    cloud_errors: int = 0
    recent_decisions: List[RoutingDecision] = field(default_factory=list)


# Routing rules: task type → preferred provider
_ROUTING_RULES: Dict[TaskType, ProviderPreference] = {
    TaskType.ROUTINE_CHAT: ProviderPreference.LOCAL,
    TaskType.LONG_FORM_SUMMARY: ProviderPreference.CLOUD,
    TaskType.PROGRESS_ANALYSIS: ProviderPreference.CLOUD,
    TaskType.KNOWLEDGE_RETRIEVAL: ProviderPreference.AUTO,
}

# Max recent decisions to keep in memory
_MAX_RECENT_DECISIONS = 100


class LLMOrchestrator:
    """
    Dual-LLM orchestrator that routes requests between local (Ollama)
    and cloud (Groq) providers with automatic fallback, PII scrubbing,
    and request-level routing metadata.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._local: Optional[BaseLLMClient] = None
        self._cloud: Optional[BaseLLMClient] = None
        self._local_available: bool = False
        self._cloud_available: bool = False
        self._scrubber = PIIScrubber(reversible=False, detect_names=True)
        self._stats = OrchestratorStats()
        self._initialized = False

        # Latency tracking (rolling averages)
        self._local_latencies: List[float] = []
        self._cloud_latencies: List[float] = []

    async def initialize(self) -> None:
        """
        Initialize both LLM clients and check their health.
        Called once during application startup.
        """
        if self._initialized:
            return

        settings = self._settings

        # Initialize local client (Ollama)
        try:
            from app.services.ollama_client import OllamaClient
            self._local = OllamaClient()
            self._local_available = await self._local.is_reachable()
            if self._local_available:
                logger.info(
                    "✅ Orchestrator: Local LLM (Ollama) ready — model=%s, url=%s",
                    self._local.model_name,
                    self._local.base_url,
                )
            else:
                logger.warning(
                    "⚠️  Orchestrator: Local LLM (Ollama) NOT reachable at %s",
                    settings.OLLAMA_BASE_URL,
                )
        except Exception as exc:
            logger.error("❌ Orchestrator: Failed to initialize Ollama client: %s", exc)
            self._local = None

        # Initialize cloud client (Groq)
        try:
            if settings.GROQ_API_KEY:
                from app.services.groq_client import GroqClient
                self._cloud = GroqClient()
                self._cloud_available = await self._cloud.is_reachable()
                if self._cloud_available:
                    logger.info(
                        "✅ Orchestrator: Cloud LLM (Groq) ready — model=%s",
                        self._cloud.model_name,
                    )
                else:
                    logger.warning("⚠️  Orchestrator: Cloud LLM (Groq) NOT reachable")
            else:
                logger.info("Orchestrator: Groq API key not set — cloud LLM disabled")
        except Exception as exc:
            logger.error("❌ Orchestrator: Failed to initialize Groq client: %s", exc)
            self._cloud = None

        if not self._local_available and not self._cloud_available:
            logger.error("❌ Orchestrator: NO LLM providers available!")

        self._initialized = True

    # ------------------------------------------------------------------
    # Routing Logic
    # ------------------------------------------------------------------

    def _select_provider(
        self,
        task_type: TaskType,
        has_pii: bool,
        force_provider: Optional[ProviderPreference] = None,
    ) -> tuple[Optional[BaseLLMClient], str, Optional[BaseLLMClient], Optional[str]]:
        """
        Select primary and fallback providers based on routing rules.

        Returns: (primary_client, primary_name, fallback_client, fallback_name)
        """
        # PII → always local, no cloud fallback
        if has_pii:
            if self._local_available and self._local:
                return self._local, "ollama", None, None
            else:
                logger.warning("PII detected but local LLM unavailable — refusing cloud")
                return None, "none", None, None

        # Forced provider
        if force_provider == ProviderPreference.LOCAL:
            primary = self._local if self._local_available else None
            fallback = self._cloud if self._cloud_available else None
            return primary, "ollama", fallback, "groq"
        elif force_provider == ProviderPreference.CLOUD:
            primary = self._cloud if self._cloud_available else None
            fallback = self._local if self._local_available else None
            return primary, "groq", fallback, "ollama"

        # Auto routing based on task type
        preference = _ROUTING_RULES.get(task_type, ProviderPreference.AUTO)

        if preference == ProviderPreference.LOCAL:
            if self._local_available and self._local:
                return (
                    self._local, "ollama",
                    self._cloud if self._cloud_available else None,
                    "groq" if self._cloud_available else None,
                )
            elif self._cloud_available and self._cloud:
                return self._cloud, "groq", None, None
        elif preference == ProviderPreference.CLOUD:
            if self._cloud_available and self._cloud:
                return (
                    self._cloud, "groq",
                    self._local if self._local_available else None,
                    "ollama" if self._local_available else None,
                )
            elif self._local_available and self._local:
                return self._local, "ollama", None, None
        else:
            # AUTO — pick whichever is available, prefer local for lower latency
            if self._local_available and self._local:
                return (
                    self._local, "ollama",
                    self._cloud if self._cloud_available else None,
                    "groq" if self._cloud_available else None,
                )
            elif self._cloud_available and self._cloud:
                return self._cloud, "groq", None, None

        return None, "none", None, None

    # ------------------------------------------------------------------
    # Generate (non-streaming)
    # ------------------------------------------------------------------

    async def generate(
        self,
        user_text: str,
        face_emotion: str = "neutral",
        history: Optional[List[ConversationMessage]] = None,
        text_emotion_summary: Optional[str] = None,
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
        task_type: TaskType = TaskType.ROUTINE_CHAT,
        force_provider: Optional[ProviderPreference] = None,
    ) -> tuple[str, PsychReport, RoutingDecision]:
        """
        Generate a response using intelligent dual-LLM routing.

        Returns: (reply_text, PsychReport, RoutingDecision)
        """
        start_time = time.monotonic()

        # PII check
        scrub_result: Optional[ScrubResult] = None
        has_pii = False
        if self._settings.PII_SCRUB_BEFORE_CLOUD:
            has_pii = self._scrubber.has_pii(user_text)

        # Select providers
        primary, primary_name, fallback, fallback_name = self._select_provider(
            task_type, has_pii, force_provider
        )

        if primary is None:
            elapsed = (time.monotonic() - start_time) * 1000
            decision = RoutingDecision(
                provider_used="none",
                task_type=task_type.value,
                latency_ms=elapsed,
                error="No LLM providers available",
            )
            self._record_decision(decision)
            return (
                "I'm sorry, but the inference service is currently unavailable. Please try again shortly.",
                fallback_report(),
                decision,
            )

        # Scrub PII if sending to cloud
        effective_text = user_text
        if primary_name == "groq" and self._settings.PII_SCRUB_BEFORE_CLOUD:
            scrub_result = self._scrubber.scrub(user_text)
            effective_text = scrub_result.scrubbed_text

        # Try primary provider
        try:
            reply, report = await primary.generate(
                user_text=effective_text,
                face_emotion=face_emotion,
                history=history,
                text_emotion_summary=text_emotion_summary,
                patient_profile=patient_profile,
                gita_context=gita_context,
            )
            elapsed = (time.monotonic() - start_time) * 1000

            decision = RoutingDecision(
                provider_used=primary_name,
                task_type=task_type.value,
                latency_ms=round(elapsed, 1),
                pii_scrubbed=scrub_result.pii_found if scrub_result else False,
                pii_types=scrub_result.pii_types if scrub_result else [],
            )
            self._record_decision(decision)
            self._update_latency(primary_name, elapsed)
            return reply, report, decision

        except Exception as exc:
            logger.error(
                "Orchestrator: Primary provider '%s' failed: %s",
                primary_name, exc,
            )
            self._record_error(primary_name)

        # Try fallback provider
        if fallback is not None and fallback_name is not None:
            logger.info(
                "Orchestrator: Falling back to '%s'", fallback_name,
            )

            # Re-scrub if fallback is cloud
            fb_text = user_text
            fb_scrub: Optional[ScrubResult] = None
            if fallback_name == "groq" and self._settings.PII_SCRUB_BEFORE_CLOUD:
                fb_scrub = self._scrubber.scrub(user_text)
                fb_text = fb_scrub.scrubbed_text
                if fb_scrub.pii_found:
                    # PII found but fallback is cloud — refuse
                    logger.warning("PII detected, refusing cloud fallback")
                    elapsed = (time.monotonic() - start_time) * 1000
                    decision = RoutingDecision(
                        provider_used="none",
                        task_type=task_type.value,
                        latency_ms=round(elapsed, 1),
                        fallback_used=True,
                        error="PII detected, cloud fallback refused",
                        pii_scrubbed=True,
                        pii_types=fb_scrub.pii_types,
                    )
                    self._record_decision(decision)
                    return (
                        "I'm sorry, but the local inference service is unavailable and your message contains sensitive information "
                        "that cannot be sent to the cloud. Please try again when the local service is restored.",
                        fallback_report(),
                        decision,
                    )

            try:
                reply, report = await fallback.generate(
                    user_text=fb_text,
                    face_emotion=face_emotion,
                    history=history,
                    text_emotion_summary=text_emotion_summary,
                    patient_profile=patient_profile,
                    gita_context=gita_context,
                )
                elapsed = (time.monotonic() - start_time) * 1000

                decision = RoutingDecision(
                    provider_used=fallback_name,
                    task_type=task_type.value,
                    latency_ms=round(elapsed, 1),
                    fallback_used=True,
                    fallback_provider=primary_name,
                    pii_scrubbed=fb_scrub.pii_found if fb_scrub else False,
                    pii_types=fb_scrub.pii_types if fb_scrub else [],
                )
                self._record_decision(decision)
                self._update_latency(fallback_name, elapsed)
                return reply, report, decision

            except Exception as exc2:
                logger.error(
                    "Orchestrator: Fallback provider '%s' also failed: %s",
                    fallback_name, exc2,
                )
                self._record_error(fallback_name)

        # Both failed
        elapsed = (time.monotonic() - start_time) * 1000
        decision = RoutingDecision(
            provider_used="none",
            task_type=task_type.value,
            latency_ms=round(elapsed, 1),
            fallback_used=True,
            error="All LLM providers failed",
        )
        self._record_decision(decision)
        return (
            "I'm sorry, but all inference services are currently unavailable. "
            "Please try again shortly.",
            fallback_report(),
            decision,
        )

    # ------------------------------------------------------------------
    # Generate (streaming)
    # ------------------------------------------------------------------

    async def generate_stream(
        self,
        user_text: str,
        face_emotion: str = "neutral",
        history: Optional[List[ConversationMessage]] = None,
        text_emotion_summary: Optional[str] = None,
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
        task_type: TaskType = TaskType.ROUTINE_CHAT,
        force_provider: Optional[ProviderPreference] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a response using intelligent dual-LLM routing.
        Fallback is attempted if the primary provider fails to connect.
        """
        has_pii = False
        if self._settings.PII_SCRUB_BEFORE_CLOUD:
            has_pii = self._scrubber.has_pii(user_text)

        primary, primary_name, fallback, fallback_name = self._select_provider(
            task_type, has_pii, force_provider
        )

        if primary is None:
            yield "\n[No LLM providers available. Please check your configuration.]\n"
            return

        effective_text = user_text
        if primary_name == "groq" and self._settings.PII_SCRUB_BEFORE_CLOUD:
            scrub_result = self._scrubber.scrub(user_text)
            effective_text = scrub_result.scrubbed_text

        try:
            async for token in primary.generate_stream(
                user_text=effective_text,
                face_emotion=face_emotion,
                history=history,
                text_emotion_summary=text_emotion_summary,
                patient_profile=patient_profile,
                gita_context=gita_context,
            ):
                yield token
            return
        except Exception as exc:
            logger.error(
                "Orchestrator stream: Primary '%s' failed: %s",
                primary_name, exc,
            )

        # Try fallback for streaming
        if fallback is not None:
            fb_text = user_text
            if fallback_name == "groq" and self._settings.PII_SCRUB_BEFORE_CLOUD:
                scrub_result = self._scrubber.scrub(user_text)
                fb_text = scrub_result.scrubbed_text

            try:
                async for token in fallback.generate_stream(
                    user_text=fb_text,
                    face_emotion=face_emotion,
                    history=history,
                    text_emotion_summary=text_emotion_summary,
                    patient_profile=patient_profile,
                    gita_context=gita_context,
                ):
                    yield token
                return
            except Exception as exc2:
                logger.error(
                    "Orchestrator stream: Fallback '%s' also failed: %s",
                    fallback_name, exc2,
                )

        yield "\n[All inference services failed. Please try again.]\n"

    # ------------------------------------------------------------------
    # Health Checks
    # ------------------------------------------------------------------

    async def refresh_health(self) -> None:
        """Re-check both providers' health status."""
        if self._local:
            self._local_available = await self._local.is_reachable()
        if self._cloud:
            self._cloud_available = await self._cloud.is_reachable()

    async def is_any_reachable(self) -> bool:
        """Returns True if at least one provider is reachable."""
        return self._local_available or self._cloud_available

    # ------------------------------------------------------------------
    # Stats & Monitoring
    # ------------------------------------------------------------------

    def _record_decision(self, decision: RoutingDecision) -> None:
        """Record a routing decision for monitoring."""
        self._stats.total_requests += 1
        if decision.provider_used == "ollama":
            self._stats.local_requests += 1
        elif decision.provider_used == "groq":
            self._stats.cloud_requests += 1
        if decision.fallback_used:
            self._stats.fallback_count += 1
        if decision.pii_scrubbed:
            self._stats.pii_scrub_count += 1

        self._stats.recent_decisions.append(decision)
        if len(self._stats.recent_decisions) > _MAX_RECENT_DECISIONS:
            self._stats.recent_decisions = self._stats.recent_decisions[-_MAX_RECENT_DECISIONS:]

    def _record_error(self, provider: str) -> None:
        """Record a provider error."""
        if provider == "ollama":
            self._stats.local_errors += 1
        elif provider == "groq":
            self._stats.cloud_errors += 1

    def _update_latency(self, provider: str, latency_ms: float) -> None:
        """Update rolling average latency for a provider."""
        if provider == "ollama":
            self._local_latencies.append(latency_ms)
            if len(self._local_latencies) > 50:
                self._local_latencies = self._local_latencies[-50:]
            self._stats.avg_local_latency_ms = round(
                sum(self._local_latencies) / len(self._local_latencies), 1
            )
        elif provider == "groq":
            self._cloud_latencies.append(latency_ms)
            if len(self._cloud_latencies) > 50:
                self._cloud_latencies = self._cloud_latencies[-50:]
            self._stats.avg_cloud_latency_ms = round(
                sum(self._cloud_latencies) / len(self._cloud_latencies), 1
            )

    def get_stats(self) -> OrchestratorStats:
        """Return current orchestrator statistics."""
        return self._stats

    def get_status(self) -> dict:
        """Return current orchestrator status for health checks."""
        return {
            "orchestrator_enabled": True,
            "local": {
                "provider": "ollama",
                "available": self._local_available,
                "model": self._local.model_name if self._local else "N/A",
                "base_url": self._local.base_url if self._local else "N/A",
            },
            "cloud": {
                "provider": "groq",
                "available": self._cloud_available,
                "model": self._cloud.model_name if self._cloud else "N/A",
                "base_url": self._cloud.base_url if self._cloud else "N/A",
            },
            "stats": {
                "total_requests": self._stats.total_requests,
                "local_requests": self._stats.local_requests,
                "cloud_requests": self._stats.cloud_requests,
                "fallback_count": self._stats.fallback_count,
                "pii_scrub_count": self._stats.pii_scrub_count,
                "avg_local_latency_ms": self._stats.avg_local_latency_ms,
                "avg_cloud_latency_ms": self._stats.avg_cloud_latency_ms,
                "local_errors": self._stats.local_errors,
                "cloud_errors": self._stats.cloud_errors,
            },
        }

    # ------------------------------------------------------------------
    # Backward-compatible properties (match BaseLLMClient interface)
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Name of the primary available provider."""
        if self._local_available:
            return "ollama"
        elif self._cloud_available:
            return "groq"
        return "none"

    @property
    def model_name(self) -> str:
        """Model name of the primary available provider."""
        if self._local_available and self._local:
            return self._local.model_name
        elif self._cloud_available and self._cloud:
            return self._cloud.model_name
        return "N/A"

    @property
    def base_url(self) -> str:
        """Base URL of the primary available provider."""
        if self._local_available and self._local:
            return self._local.base_url
        elif self._cloud_available and self._cloud:
            return self._cloud.base_url
        return "N/A"

    async def is_reachable(self) -> bool:
        """Returns True if at least one provider is reachable."""
        return await self.is_any_reachable()

    async def close(self) -> None:
        """Close both provider connections."""
        if self._local:
            await self._local.close()
        if self._cloud:
            await self._cloud.close()
        logger.info("Orchestrator: All LLM clients closed.")


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_orchestrator: Optional[LLMOrchestrator] = None


def get_orchestrator() -> LLMOrchestrator:
    """Get or create the orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LLMOrchestrator()
    return _orchestrator
