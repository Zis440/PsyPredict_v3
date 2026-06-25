"""
ollama_client.py — Local Ollama LLM Client for PsyPredict

Calls a locally-running Ollama server via its HTTP API (/api/chat).
Designed for local development — no cloud API keys required.

Features:
  - Ollama /api/chat endpoint (chat-completion format)
  - NDJSON streaming support
  - Longer timeouts for CPU inference
  - Retry with exponential backoff
  - Health check via /api/tags
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator, List, Optional

import httpx

from app.config import get_settings
from app.schemas import ConversationMessage, PsychReport, fallback_report
from app.services.base_llm_client import BaseLLMClient
from app.services.llm_shared import build_messages, parse_response

logger = logging.getLogger(__name__)


class OllamaClient(BaseLLMClient):
    """
    LLM client backed by a local Ollama server.
    Uses Ollama's native /api/chat endpoint (not OpenAI-compatible mode).
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._settings.OLLAMA_MODEL_NAME

    @property
    def base_url(self) -> str:
        return self._settings.OLLAMA_BASE_URL

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_client(self, stream: bool = False) -> httpx.AsyncClient:
        # Ollama on CPU can be very slow — use generous timeouts
        read_timeout = None if stream else float(self._settings.OLLAMA_TIMEOUT_S)
        return httpx.AsyncClient(
            base_url=self._settings.OLLAMA_BASE_URL,
            timeout=httpx.Timeout(
                connect=10.0,
                read=read_timeout,
                write=30.0,
                pool=5.0,
            ),
        )

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def is_reachable(self) -> bool:
        """Returns True if the Ollama server is reachable and responding."""
        try:
            async with self._make_client() as client:
                resp = await client.get("/api/tags", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        """No persistent connections to clean up."""
        pass

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
        semantic_memories: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> tuple[str, PsychReport]:
        if history is None:
            history = []

        messages = build_messages(
            user_text, face_emotion, history,
            max_turns=self._settings.MAX_CONTEXT_TURNS,
            text_emotion_summary=text_emotion_summary,
            patient_profile=patient_profile,
            semantic_memories=semantic_memories,
            gita_context=gita_context,
        )

        payload = {
            "model": self._settings.OLLAMA_MODEL_NAME,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096,
                "top_p": 0.92,
            },
        }

        last_error: Optional[Exception] = None
        delay = self._settings.OLLAMA_RETRY_DELAY_S

        for attempt in range(1, self._settings.OLLAMA_RETRIES + 1):
            try:
                logger.info(
                    "Ollama generate attempt %d/%d (model=%s)",
                    attempt, self._settings.OLLAMA_RETRIES,
                    self._settings.OLLAMA_MODEL_NAME,
                )
                async with self._make_client() as client:
                    resp = await client.post("/api/chat", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    raw_text: str = data["message"]["content"]
                    return parse_response(raw_text)

            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning("Ollama timeout on attempt %d: %s", attempt, exc)
            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.error(
                    "Ollama HTTP error %s: %s",
                    exc.response.status_code,
                    exc.response.text[:500],
                )
                # If model not found, don't retry
                if exc.response.status_code == 404:
                    logger.error(
                        "Model '%s' not found in Ollama. Run: ollama pull %s",
                        self._settings.OLLAMA_MODEL_NAME,
                        self._settings.OLLAMA_MODEL_NAME,
                    )
                    break
            except httpx.ConnectError as exc:
                last_error = exc
                logger.error(
                    "Cannot connect to Ollama at %s — is it running? "
                    "Start with: ollama serve",
                    self._settings.OLLAMA_BASE_URL,
                )
                break  # No point retrying if server is down
            except Exception as exc:
                last_error = exc
                logger.error("Ollama unexpected error: %s", exc)

            if attempt < self._settings.OLLAMA_RETRIES:
                await asyncio.sleep(delay)
                delay *= 2

        logger.error("All Ollama attempts failed. Last error: %s", last_error)
        return (
            "The local inference service (Ollama) is temporarily unavailable. "
            "Please check that Ollama is running: ollama serve",
            fallback_report(),
        )

    # ------------------------------------------------------------------
    # Generate (streaming) — Ollama uses NDJSON, not SSE
    # ------------------------------------------------------------------

    async def generate_stream(
        self,
        user_text: str,
        face_emotion: str = "neutral",
        history: Optional[List[ConversationMessage]] = None,
        text_emotion_summary: Optional[str] = None,
        patient_profile: Optional[str] = None,
        semantic_memories: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> AsyncIterator[str]:
        if history is None:
            history = []

        messages = build_messages(
            user_text, face_emotion, history,
            max_turns=self._settings.MAX_CONTEXT_TURNS,
            text_emotion_summary=text_emotion_summary,
            patient_profile=patient_profile,
            semantic_memories=semantic_memories,
            gita_context=gita_context,
        )

        payload = {
            "model": self._settings.OLLAMA_MODEL_NAME,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096,
                "top_p": 0.92,
            },
        }

        try:
            async with self._make_client(stream=True) as client:
                async with client.stream("POST", "/api/chat", json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            if token:
                                yield token
                            if chunk.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            logger.error(
                "Cannot connect to Ollama at %s for streaming. Is it running?",
                self._settings.OLLAMA_BASE_URL,
            )
            yield "\n[Ollama is not reachable. Start with: ollama serve]\n"
        except Exception as exc:
            logger.error("Ollama streaming failed: %s", exc)
            yield "\n[Inference error — Ollama request failed. Try again.]\n"
