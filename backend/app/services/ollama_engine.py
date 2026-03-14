"""
ollama_engine.py — PsyPredict LLM Engine (Groq / Llama3.3-70B)
Replaces Ollama with Groq's API. Same interface — no other files need changing.
Features:
  - Groq API via httpx (OpenAI-compatible endpoint)
  - Structured JSON output via ---JSON--- marker + PsychReport schema
  - Streaming support
  - Retry with exponential backoff
  - Graceful fallback if API key missing or Groq unreachable
"""
from __future__ import annotations

import asyncio
import json
import logging
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
# Groq API base URL (OpenAI-compatible)
# ---------------------------------------------------------------------------
GROQ_API_BASE = "https://api.groq.com/openai/v1"

# ---------------------------------------------------------------------------
# System Prompt
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
# FACE → DISTRESS SCORE mapping
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
    LLM engine backed by Groq API (Llama3.3-70B).
    Named OllamaEngine to preserve all existing imports across the codebase.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

    def _make_client(self, stream: bool = False) -> httpx.AsyncClient:
        read_timeout = None if stream else float(self.settings.OLLAMA_TIMEOUT_S)
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
        if not self.settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set.")
            return False
        try:
            async with self._make_client() as client:
                resp = await client.get("/models", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Context Window Trimming
    # ------------------------------------------------------------------

    def _trim_history(
        self, history: List[ConversationMessage]
    ) -> List[ConversationMessage]:
        max_turns = self.settings.MAX_CONTEXT_TURNS
        if len(history) <= max_turns * 2:
            return history
        return history[-(max_turns * 2):]

    # ------------------------------------------------------------------
    # Messages Builder (Groq uses chat format, not raw prompt)
    # ------------------------------------------------------------------

    def _build_messages(
        self,
        user_text: str,
        face_emotion: str,
        history: List[ConversationMessage],
        text_emotion_summary: Optional[str] = None,
    ) -> list:
        """
        Builds the messages array for Groq's chat completions API.
        System prompt is a dedicated system message.
        History becomes alternating user/assistant messages.
        Multimodal context is appended to the final user message.
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        trimmed = self._trim_history(history)
        for msg in trimmed:
            messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })

        face_distress = FACE_DISTRESS_MAP.get(face_emotion.lower(), 0.20)
        multimodal_ctx = (
            f"\n\n[MULTIMODAL CONTEXT]\n"
            f"Face emotion (webcam): {face_emotion} (distress score: {face_distress:.2f})\n"
        )
        if text_emotion_summary:
            multimodal_ctx += f"Text emotion (DistilBERT): {text_emotion_summary}\n"

        final_user_content = user_text + multimodal_ctx
        messages.append({"role": "user", "content": final_user_content})

        return messages

    # ------------------------------------------------------------------
    # Parse LLM Output → (reply_text, PsychReport)
    # ------------------------------------------------------------------

    def _parse_response(self, raw: str) -> tuple[str, PsychReport]:
        marker = "---JSON---"
        if marker in raw:
            parts = raw.split(marker, 1)
            reply_text = parts[0].strip()
            json_block = parts[1].strip()
        else:
            reply_text = ""
            json_block = raw.strip()

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
                "Failed to parse PsychReport from Groq output: %s | raw=%r",
                exc,
                json_block[:500],
            )
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
        if not self.settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — returning fallback.")
            return ("Groq API key is not configured.", fallback_report())

        if history is None:
            history = []

        messages = self._build_messages(user_text, face_emotion, history, text_emotion_summary)

        payload = {
            "model": self.settings.GROQ_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
            "stream": False,
        }

        last_error: Optional[Exception] = None
        delay = self.settings.OLLAMA_RETRY_DELAY_S

        for attempt in range(1, self.settings.OLLAMA_RETRIES + 1):
            try:
                logger.info("Groq generate attempt %d/%d", attempt, self.settings.OLLAMA_RETRIES)
                async with self._make_client() as client:
                    resp = await client.post("/chat/completions", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    raw_text: str = data["choices"][0]["message"]["content"]
                    return self._parse_response(raw_text)

            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning("Groq timeout on attempt %d: %s", attempt, exc)
            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.error("Groq HTTP error %s: %s", exc.response.status_code, exc.response.text)
                break
            except Exception as exc:
                last_error = exc
                logger.error("Groq unexpected error: %s", exc)

            if attempt < self.settings.OLLAMA_RETRIES:
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
    ) -> AsyncIterator[str]:
        if not self.settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — returning fallback stream.")
            yield "Groq API key is not configured.\n---JSON---\n" + json.dumps(fallback_report().model_dump())
            return

        if history is None:
            history = []

        messages = self._build_messages(user_text, face_emotion, history, text_emotion_summary)

        payload = {
            "model": self.settings.GROQ_MODEL,
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


# ---------------------------------------------------------------------------
# Singleton — same name so all existing imports work unchanged
# ---------------------------------------------------------------------------
ollama_engine = OllamaEngine()
