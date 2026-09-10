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
            "User-Agent": "PsyPredict/1.0",
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
        semantic_memories: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> tuple[str, PsychReport]:
        if not self._settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — returning fallback report.")
            return (
                "Groq API key is not configured. Please set GROQ_API_KEY in your environment.",
                fallback_report(),
            )

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

        models_to_try = [self._settings.GROQ_MODEL]
        for fallback_m in ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
            if fallback_m not in models_to_try:
                models_to_try.append(fallback_m)

        for model_name in models_to_try:
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 1024,
                "stream": False,
            }
            try:
                logger.info("Groq generate attempt with model '%s'", model_name)
                async with self._make_client() as client:
                    resp = await client.post("/chat/completions", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    raw_text: str = data["choices"][0]["message"]["content"]
                    return parse_response(raw_text)

            except httpx.HTTPStatusError as exc:
                logger.warning("Groq model '%s' failed with HTTP %s: %s", model_name, exc.response.status_code, exc.response.text[:120])
                continue
            except Exception as exc:
                logger.error("Groq unexpected error with model '%s': %s", model_name, exc)
                continue

        logger.error("All Groq candidate models failed.")
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
        semantic_memories: Optional[str] = None,
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
            semantic_memories=semantic_memories,
            gita_context=gita_context,
        )

        models_to_try = [self._settings.GROQ_MODEL]
        for fallback_m in ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
            if fallback_m not in models_to_try:
                models_to_try.append(fallback_m)

        for model_name in models_to_try:
            payload = {
                "model": model_name,
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
                return
            except Exception as exc:
                logger.warning("Groq stream model '%s' failed: %s", model_name, exc)
                continue

        yield "\n[Inference error — Groq request failed. Try again.]\n"
