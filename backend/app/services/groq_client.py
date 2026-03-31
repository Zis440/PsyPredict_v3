"""
groq_client.py — Groq Cloud LLM Client for PsyPredict

Calls Groq's OpenAI-compatible API (api.groq.com) for Llama3 inference.
This is the default provider for the Hugging Face Spaces deployment.

Features:
  - OpenAI-compatible /chat/completions endpoint
  - Streaming via SSE (Server-Sent Events)
  - Retry with exponential backoff
  - Graceful fallback when API key is missing
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

# ---------------------------------------------------------------------------
# Groq API base URL (OpenAI-compatible)
# ---------------------------------------------------------------------------
GROQ_API_BASE = "https://api.groq.com/openai/v1"


class GroqClient(BaseLLMClient):
    """
    LLM client backed by Groq API (Llama 3.3 70B).
    Uses the OpenAI-compatible /chat/completions endpoint.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return self._settings.GROQ_MODEL

    @property
    def base_url(self) -> str:
        return GROQ_API_BASE

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

    def _make_client(self, stream: bool = False) -> httpx.AsyncClient:
        read_timeout = None if stream else float(self._settings.OLLAMA_TIMEOUT_S)
        return httpx.AsyncClient(
            base_url=GROQ_API_BASE,
            headers=self._headers(),
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
        """Returns True if Groq API key is set and endpoint is reachable."""
        if not self._settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set.")
            return False
        try:
            async with self._make_client() as client:
                resp = await client.get("/models", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        """No persistent connections to clean up for Groq."""
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
        gita_context: Optional[str] = None,
    ) -> tuple[str, PsychReport]:
        if not self._settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — returning fallback.")
            return ("Groq API key is not configured.", fallback_report())

        if history is None:
            history = []

        messages = build_messages(
            user_text, face_emotion, history,
            max_turns=self._settings.MAX_CONTEXT_TURNS,
            text_emotion_summary=text_emotion_summary,
            patient_profile=patient_profile,
            gita_context=gita_context,
        )

        payload = {
            "model": self._settings.GROQ_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
            "stream": False,
        }

        last_error: Optional[Exception] = None
        delay = self._settings.OLLAMA_RETRY_DELAY_S

        for attempt in range(1, self._settings.OLLAMA_RETRIES + 1):
            try:
                logger.info("Groq generate attempt %d/%d", attempt, self._settings.OLLAMA_RETRIES)
                async with self._make_client() as client:
                    resp = await client.post("/chat/completions", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    raw_text: str = data["choices"][0]["message"]["content"]
                    return parse_response(raw_text)

            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning("Groq timeout on attempt %d: %s", attempt, exc)
            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.error("Groq HTTP error %s: %s", exc.response.status_code, exc.response.text)
                break  # Don't retry on HTTP errors (auth, rate limit, etc.)
            except Exception as exc:
                last_error = exc
                logger.error("Groq unexpected error: %s", exc)

            if attempt < self._settings.OLLAMA_RETRIES:
                await asyncio.sleep(delay)
                delay *= 2

        logger.error("All Groq attempts failed. Last error: %s", last_error)
        return ("The inference service is temporarily unavailable. Please try again shortly.", fallback_report())

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
    ) -> AsyncIterator[str]:
        if not self._settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — returning fallback stream.")
            yield "Groq API key is not configured.\n---JSON---\n" + json.dumps(fallback_report().model_dump())
            return

        if history is None:
            history = []

        messages = build_messages(
            user_text, face_emotion, history,
            max_turns=self._settings.MAX_CONTEXT_TURNS,
            text_emotion_summary=text_emotion_summary,
            patient_profile=patient_profile,
            gita_context=gita_context,
        )

        payload = {
            "model": self._settings.GROQ_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
            "stream": True,
        }

        try:
            async with self._make_client(stream=True) as client:
                async with client.stream("POST", "/chat/completions", json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data_str = line[len("data: "):]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            token = chunk["choices"][0].get("delta", {}).get("content", "")
                            if token:
                                yield token
                        except (json.JSONDecodeError, KeyError):
                            continue
        except Exception as exc:
            logger.error("Groq streaming failed: %s", exc)
            yield "\n[Inference error — Groq request failed. Try again.]\n"
