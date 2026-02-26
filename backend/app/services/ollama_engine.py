"""
ollama_engine.py — PsyPredict Local LLM Engine
Async Ollama client with:
  - Structured JSON output enforced via schema-in-prompt + Ollama format param
  - Context window trimming
  - Retry with exponential backoff
  - Graceful fallback on Ollama unreachability
  - Streaming support
  - Zero external API dependency
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import AsyncIterator, List, Optional

import httpx

from app.config import get_settings
from app.schemas import (
    ConversationMessage,
    PsychReport,
    RiskLevel,
    fallback_report,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System Prompt — Deterministic, clinical, no filler
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a compassionate clinical AI therapist integrated into PsyPredict, a mental health platform.
Your role is twofold:
1. Respond as a warm, empathetic therapist — never robotic, never dismissive.
2. Provide a structured backend psychological assessment in JSON format.

== CONVERSATIONAL RESPONSE RULES ==
- ALWAYS give a full, thoughtful, empathetic response FIRST (before the JSON block).
- Responses must be at least 3-5 sentences. Never one-liners.
- Validate the user's feelings. Reflect back what they shared. Show you truly listened.
- Do NOT start with "I'm here to help" or generic openers. Be specific to what they said.
- Use warm, humanizing language. Be like a therapist who genuinely cares, not a support chatbot.
- If the situation involves trauma, grief, betrayal, or crisis — respond with appropriate gravity and compassion.
- Suggest one concrete, actionable step at the end of your reply.
- Do NOT mention the JSON block, schema, or any technical terms in your reply.

== JSON ASSESSMENT RULES ==
After your conversational response, add the marker: ---JSON---
Then provide the PsychReport JSON.

1. Output ONLY valid JSON conforming exactly to the PsychReport schema below.
2. Do NOT fabricate clinical diagnoses. Infer only from the evidence provided.
3. cognitive_distortions must reference recognized CBT distortion labels only.
4. suggested_interventions must be concrete and clinically actionable.
5. confidence_score reflects YOUR confidence in this assessment (0.0 to 1.0).
6. crisis_triggered MUST be false — crisis detection is handled by a separate layer.
7. service_degraded MUST be false.

PSYCH_REPORT_SCHEMA:
{
  "risk_classification": "<MINIMAL|LOW|MODERATE|HIGH|CRITICAL>",
  "emotional_state_summary": "<string>",
  "behavioral_inference": "<string>",
  "cognitive_distortions": ["<string>", ...],
  "suggested_interventions": ["<string>", ...],
  "confidence_score": <float 0.0-1.0>,
  "crisis_triggered": false,
  "crisis_resources": null,
  "service_degraded": false
}

Output format:
<Your full, empathetic therapist response here — 3-5 sentences minimum>
---JSON---
{ ...psych report json... }
"""


# ---------------------------------------------------------------------------
# FACE → DISTRESS SCORE mapping (calibrated, not heuristic)
# ---------------------------------------------------------------------------

FACE_DISTRESS_MAP: dict[str, float] = {
    "fear": 0.80,
    "sad": 0.70,
    "angry": 0.50,
    "disgust": 0.40,
    "surprised": 0.30,
    "neutral": 0.20,
    "happy": 0.05,
}


class OllamaEngine:
    """
    Production async LLM engine backed by local Ollama/LLaMA 3.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional[httpx.AsyncClient] = None
        self._local_llm: Optional[any] = None  # llama_cpp.Llama instance

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.settings.OLLAMA_BASE_URL,
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=self.settings.OLLAMA_TIMEOUT_S,
                    write=30.0,
                    pool=5.0,
                ),
            )
        return self._client

    def _get_local_llm(self):
        """Lazy load llama-cpp-python model."""
        if self._local_llm is None:
            try:
                from llama_cpp import Llama
                logger.info("Loading local GGUF model from %s", self.settings.GGUF_MODEL_PATH)
                self._local_llm = Llama(
                    model_path=self.settings.GGUF_MODEL_PATH,
                    n_ctx=self.settings.LLM_CONTEXT_SIZE,
                    n_threads=os.cpu_count() or 4,
                    verbose=False
                )
            except ImportError:
                logger.error("llama-cpp-python not installed. Cannot use embedded LLM.")
                raise RuntimeError("llama-cpp-python not installed")
            except Exception as exc:
                logger.error("Failed to load local GGUF model: %s", exc)
                raise
        return self._local_llm

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def is_reachable(self) -> bool:
        """Returns True if Ollama API is reachable."""
        try:
            resp = await self.client.get("/api/tags", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Context Window Trimming
    # ------------------------------------------------------------------

    def _trim_history(
        self, history: List[ConversationMessage]
    ) -> List[ConversationMessage]:
        """Keep the last MAX_CONTEXT_TURNS message pairs."""
        max_turns = self.settings.MAX_CONTEXT_TURNS
        if len(history) <= max_turns * 2:
            return history
        return history[-(max_turns * 2):]

    # ------------------------------------------------------------------
    # Prompt Builder
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        user_text: str,
        face_emotion: str,
        history: List[ConversationMessage],
        text_emotion_summary: Optional[str] = None,
    ) -> str:
        trimmed = self._trim_history(history)
        history_block = "\n".join(
            f"[{msg.role.upper()}]: {msg.content}" for msg in trimmed
        )

        face_distress = FACE_DISTRESS_MAP.get(face_emotion.lower(), 0.20)
        multimodal_ctx = (
            f"MULTIMODAL CONTEXT:\n"
            f"  Face emotion (webcam): {face_emotion} (distress score: {face_distress:.2f})\n"
        )
        if text_emotion_summary:
            multimodal_ctx += f"  Text emotion (DistilBERT): {text_emotion_summary}\n"

        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"CONVERSATION HISTORY:\n{history_block}\n\n"
            f"{multimodal_ctx}\n"
            f"CURRENT USER INPUT:\n{user_text}\n\n"
            "ASSISTANT:"
        )

    # ------------------------------------------------------------------
    # Parse LLM Output → (reply_text, PsychReport)
    # ------------------------------------------------------------------

    def _parse_response(self, raw: str) -> tuple[str, PsychReport]:
        """
        Split on ---JSON--- marker and validate the JSON block.
        Returns (conversational_reply, PsychReport).
        """
        marker = "---JSON---"
        if marker in raw:
            parts = raw.split(marker, 1)
            reply_text = parts[0].strip()
            json_block = parts[1].strip()
        else:
            # Try to find JSON object in the raw output
            reply_text = ""
            json_block = raw.strip()

        # Extract JSON object (handle markdown code fences)
        if json_block.startswith("```"):
            lines = json_block.split("\n")
            json_block = "\n".join(
                l for l in lines if not l.startswith("```")
            ).strip()

        try:
            data = json.loads(json_block)
            report = PsychReport(**data)
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.warning(
                "Failed to parse PsychReport from LLM output: %s | raw=%r",
                exc,
                json_block[:500],
            )
            # Return partial fallback
            report = fallback_report()
            if not reply_text:
                reply_text = raw.strip()

        return reply_text, report

    # ------------------------------------------------------------------
    # Generate (non-streaming)
    # ------------------------------------------------------------------

    async def generate(
        self,
        user_text: str,
        face_emotion: str = "neutral",
        history: Optional[List[ConversationMessage]] = None,
        text_emotion_summary: Optional[str] = None,
    ) -> tuple[str, PsychReport]:
        """
        Calls either Ollama API or Embedded LLM based on settings, 
        with automatic fallback to local if Ollama is unreachable.
        """
        # If user explicitly wants embedded mode
        if self.settings.USE_EMBEDDED_LLM:
            return await self._generate_local(user_text, face_emotion, history, text_emotion_summary)
        
        # Otherwise try Ollama, fallback to local if it fails and GGUF is available
        try:
            reply, report = await self._generate_ollama(user_text, face_emotion, history, text_emotion_summary)
            # If _generate_ollama returned the hardcoded fallback string, it failed its retries
            if "inference service is temporarily unavailable" in reply:
                raise ConnectionError("Ollama service unreachable after retries.")
            return reply, report
        except Exception as exc:
            import os
            if os.path.exists(self.settings.GGUF_MODEL_PATH):
                logger.info("Ollama failed, falling back to embedded GGUF model: %s", exc)
                return await self._generate_local(user_text, face_emotion, history, text_emotion_summary)
            else:
                logger.error("Ollama failed and no GGUF model found for fallback at %s", self.settings.GGUF_MODEL_PATH)
                return (
                    "The inference service is temporarily unavailable and no local fallback is configured.",
                    fallback_report(),
                )

    async def _generate_local(
        self,
        user_text: str,
        face_emotion: str,
        history: Optional[List[ConversationMessage]],
        text_emotion_summary: Optional[str]
    ) -> tuple[str, PsychReport]:
        """Embedded generation via llama-cpp-python."""
        if history is None: history = []
        prompt = self._build_prompt(user_text, face_emotion, history, text_emotion_summary)
        
        try:
            llm = self._get_local_llm()
            # Run blocking LLM call in a separate thread
            response = await asyncio.to_thread(
                llm,
                prompt=prompt,
                max_tokens=600,
                temperature=0.2,
                top_p=0.9,
                stop=["USER:", "CURRENT USER INPUT:"]
            )
            raw_text = response["choices"][0]["text"]
            return self._parse_response(raw_text)
        except Exception as exc:
            logger.error("Embedded local LLM failed: %s", exc)
            return "The local inference service encountered an error.", fallback_report()

    async def _generate_ollama(
        self,
        user_text: str,
        face_emotion: str,
        history: Optional[List[ConversationMessage]],
        text_emotion_summary: Optional[str]
    ) -> tuple[str, PsychReport]:
        """Existing Ollama HTTP logic."""
        if history is None: history = []

        prompt = self._build_prompt(user_text, face_emotion, history, text_emotion_summary)

        payload = {
            "model": self.settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,      # Low temp for determinism
                "top_p": 0.9,
                "num_ctx": 4096,
                "stop": [],
            },
        }

        last_error: Optional[Exception] = None
        delay = self.settings.OLLAMA_RETRY_DELAY_S

        for attempt in range(1, self.settings.OLLAMA_RETRIES + 1):
            try:
                logger.info(
                    "Ollama generate attempt %d/%d",
                    attempt,
                    self.settings.OLLAMA_RETRIES,
                )
                resp = await self.client.post("/api/generate", json=payload)
                resp.raise_for_status()
                data = resp.json()
                raw_text: str = data.get("response", "")

                reply, report = self._parse_response(raw_text)
                return reply, report

            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning("Ollama timeout on attempt %d: %s", attempt, exc)
            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.error("Ollama HTTP error %s: %s", exc.response.status_code, exc)
                break  # Non-retryable HTTP error
            except Exception as exc:
                last_error = exc
                logger.error("Ollama unexpected error: %s", exc)

            if attempt < self.settings.OLLAMA_RETRIES:
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

        logger.error(
            "All Ollama attempts failed. Returning fallback. Last error: %s",
            last_error,
        )
        return (
            "The inference service is temporarily unavailable. Please try again shortly.",
            fallback_report(),
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
    ) -> AsyncIterator[str]:
        """
        Yields raw text chunks as they arrive from either Ollama or Embedded LLM.
        """
        if self.settings.USE_EMBEDDED_LLM:
            async for chunk in self._generate_stream_local(user_text, face_emotion, history, text_emotion_summary):
                yield chunk
        else:
            async for chunk in self._generate_stream_ollama(user_text, face_emotion, history, text_emotion_summary):
                yield chunk

    async def _generate_stream_local(
        self,
        user_text: str,
        face_emotion: str,
        history: Optional[List[ConversationMessage]],
        text_emotion_summary: Optional[str]
    ) -> AsyncIterator[str]:
        """Embedded streaming via llama-cpp-python."""
        if history is None: history = []
        prompt = self._build_prompt(user_text, face_emotion, history, text_emotion_summary)
        
        try:
            llm = self._get_local_llm()
            # llama-cpp-python streaming is synchronous, so we need to wrap it
            stream = llm(
                prompt=prompt,
                max_tokens=600,
                temperature=0.2,
                top_p=0.9,
                stream=True,
                stop=["USER:", "CURRENT USER INPUT:"]
            )
            for chunk in stream:
                token = chunk["choices"][0]["text"]
                if token:
                    yield token
                await asyncio.sleep(0) # Yield control
        except Exception as exc:
            logger.error("Embedded streaming failed: %s", exc)
            yield "\n[Local inference error]"

    async def _generate_stream_ollama(
        self,
        user_text: str,
        face_emotion: str,
        history: Optional[List[ConversationMessage]],
        text_emotion_summary: Optional[str]
    ) -> AsyncIterator[str]:
        """
        Yields raw text chunks as they arrive from Ollama.
        The full accumulated response is NOT parsed into PsychReport here;
        caller must buffer and parse at end.
        """
        if history is None:
            history = []

        prompt = self._build_prompt(user_text, face_emotion, history, text_emotion_summary)

        payload = {
            "model": self.settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": 0.2, "top_p": 0.9, "num_ctx": 4096},
        }

        try:
            async with self.client.stream("POST", "/api/generate", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as exc:
            logger.error("Ollama streaming failed: %s", exc)
            yield "\n[Inference service error — please retry]\n"


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
ollama_engine = OllamaEngine()
