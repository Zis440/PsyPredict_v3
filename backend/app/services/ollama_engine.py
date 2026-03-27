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

SYSTEM_PROMPT = """You are PsyPredict — a licensed clinical psychologist with deep expertise in CBT, DBT, psychodynamic therapy, and the psychological wisdom of the Bhagavad Gita. You combine modern evidence-based psychology with ancient Vedic insight to help each person heal.

Your role is twofold:
1. Respond as a warm, deeply insightful psychologist who truly understands human suffering.
2. Provide a structured backend psychological assessment in JSON format.

== CONVERSATIONAL RESPONSE RULES ==
- ALWAYS give a full, thoughtful, deeply empathetic response FIRST (before the JSON block).
- Responses must be at least 4-7 sentences. Never one-liners or generic platitudes.
- Validate the user's feelings FIRST. Reflect back what they shared. Show you truly listened.
- Do NOT start with "I'm here to help" or generic openers. Be specific to what they said.
- Use warm, humanizing language — like a wise, caring psychologist talking to someone they deeply care about.
- If the situation involves trauma, grief, betrayal, or crisis — respond with appropriate gravity, compassion, and clinical depth.

== GITA SHLOKA INTEGRATION RULES ==
- When a Gita shloka is provided in the GITA WISDOM CONTEXT below, you MUST weave it into your response naturally.
- Quote the shloka reference (e.g., "Gita, Chapter 2, Verse 47") and explain it in SIMPLE, HUMANIZED language.
- Include the original SANSKRIT TERM (e.g., Titiksha, Sthita-prajna, Vairagya) alongside plain English meaning.
- Explain HOW this ancient wisdom DIRECTLY applies to the user's SPECIFIC situation — not generic advice.
- Use real-life analogies, metaphors, or stories to make the shloka relatable and memorable.
- NEVER repeat the same shloka explanation verbatim across responses. Use fresh angles, analogies, and framing each time.
- If no shloka is provided, you may still reference Gita wisdom from your knowledge, but always be specific.

== PATIENT HISTORY & ADAPTIVE RULES ==
- If PATIENT HISTORY is provided below, use it to personalize your response.
- Reference progress or patterns you notice (e.g., "I can see from our past conversations that...").
- Adapt your therapeutic approach based on what has worked or not worked before.
- If the patient is improving, acknowledge and reinforce the progress.
- If the patient is recurring in distress, gently explore deeper root causes.
- Be a psychologist who REMEMBERS — this builds trust and therapeutic alliance.

== THERAPEUTIC DEPTH ==
- End each response with ONE concrete, actionable psychological homework (e.g., "Tonight, try writing down three things that went well today — even small ones.").
- Use CBT reframing, DBT distress tolerance, or psychodynamic insight as appropriate.
- Vary your therapeutic approach across responses — don't always use the same framework.
- Be DIVERSE in your analogies, tone, and framing. Never give a formulaic or robotic answer.

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
<Your full, empathetic psychologist response here — 4-7 sentences minimum, with Gita shloka woven in naturally>
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
<<<<<<< HEAD
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> str:
=======
    ) -> list:
        """
        Builds the messages array for Groq's chat completions API.
        System prompt is a dedicated system message.
        History becomes alternating user/assistant messages.
        Multimodal context is appended to the final user message.
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

>>>>>>> e0df7c7515413c00067c58471d916a2c19ab0679
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

<<<<<<< HEAD
        # Patient adaptive context
        patient_ctx = ""
        if patient_profile:
            patient_ctx = f"PATIENT HISTORY (Adaptive Context — use this to personalize your response):\n{patient_profile}\n\n"

        # Gita shloka context from CSV corpus
        gita_ctx = ""
        if gita_context:
            gita_ctx = (
                f"GITA WISDOM CONTEXT (weave this shloka into your response naturally):\n"
                f"{gita_context}\n\n"
            )

        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"{patient_ctx}"
            f"{gita_ctx}"
            f"CONVERSATION HISTORY:\n{history_block}\n\n"
            f"{multimodal_ctx}\n"
            f"CURRENT USER INPUT:\n{user_text}\n\n"
            "ASSISTANT:"
        )
=======
        final_user_content = user_text + multimodal_ctx
        messages.append({"role": "user", "content": final_user_content})

        return messages
>>>>>>> e0df7c7515413c00067c58471d916a2c19ab0679

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
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> tuple[str, PsychReport]:
<<<<<<< HEAD
        """
        Calls either Ollama API or Embedded LLM based on settings, 
        with automatic fallback to local if Ollama is unreachable.
        """
        # If user explicitly wants embedded mode
        if self.settings.USE_EMBEDDED_LLM:
            return await self._generate_local(user_text, face_emotion, history, text_emotion_summary, patient_profile, gita_context)
        
        # Otherwise try Ollama, fallback to local if it fails and GGUF is available
        try:
            reply, report = await self._generate_ollama(user_text, face_emotion, history, text_emotion_summary, patient_profile, gita_context)
            # If _generate_ollama returned the hardcoded fallback string, it failed its retries
            if "inference service is temporarily unavailable" in reply:
                raise ConnectionError("Ollama service unreachable after retries.")
            return reply, report
        except Exception as exc:
            import os
            if os.path.exists(self.settings.GGUF_MODEL_PATH):
                logger.info("Ollama failed, falling back to embedded GGUF model: %s", exc)
                return await self._generate_local(user_text, face_emotion, history, text_emotion_summary, patient_profile, gita_context)
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
        text_emotion_summary: Optional[str],
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> tuple[str, PsychReport]:
        """Embedded generation via llama-cpp-python."""
        if history is None: history = []
        prompt = self._build_prompt(user_text, face_emotion, history, text_emotion_summary, patient_profile, gita_context)
        
        try:
            llm = self._get_local_llm()
            # Run blocking LLM call in a separate thread
            response = await asyncio.to_thread(
                llm,
                prompt=prompt,
                max_tokens=800,
                temperature=0.55,
                top_p=0.92,
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
        text_emotion_summary: Optional[str],
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> tuple[str, PsychReport]:
        """Existing Ollama HTTP logic."""
        if history is None: history = []

        prompt = self._build_prompt(user_text, face_emotion, history, text_emotion_summary, patient_profile, gita_context)
=======
        if not self.settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — returning fallback.")
            return ("Groq API key is not configured.", fallback_report())

        if history is None:
            history = []

        messages = self._build_messages(user_text, face_emotion, history, text_emotion_summary)
>>>>>>> e0df7c7515413c00067c58471d916a2c19ab0679

        payload = {
            "model": self.settings.GROQ_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
            "stream": False,
<<<<<<< HEAD
            "options": {
                "temperature": 0.55,
                "top_p": 0.92,
                "num_ctx": 4096,
                "stop": [],
            },
=======
>>>>>>> e0df7c7515413c00067c58471d916a2c19ab0679
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
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> AsyncIterator[str]:
<<<<<<< HEAD
        """
        Yields raw text chunks as they arrive from either Ollama or Embedded LLM.
        """
        if self.settings.USE_EMBEDDED_LLM:
            async for chunk in self._generate_stream_local(user_text, face_emotion, history, text_emotion_summary, patient_profile, gita_context):
                yield chunk
        else:
            async for chunk in self._generate_stream_ollama(user_text, face_emotion, history, text_emotion_summary, patient_profile, gita_context):
                yield chunk

    async def _generate_stream_local(
        self,
        user_text: str,
        face_emotion: str,
        history: Optional[List[ConversationMessage]],
        text_emotion_summary: Optional[str],
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Embedded streaming via llama-cpp-python."""
        if history is None: history = []
        prompt = self._build_prompt(user_text, face_emotion, history, text_emotion_summary, patient_profile, gita_context)
        
        try:
            llm = self._get_local_llm()
            # llama-cpp-python streaming is synchronous, so we need to wrap it
            stream = llm(
                prompt=prompt,
                max_tokens=800,
                temperature=0.55,
                top_p=0.92,
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
        text_emotion_summary: Optional[str],
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Yields raw text chunks as they arrive from Ollama.
        The full accumulated response is NOT parsed into PsychReport here;
        caller must buffer and parse at end.
        """
        if history is None:
            history = []

        prompt = self._build_prompt(user_text, face_emotion, history, text_emotion_summary, patient_profile, gita_context)
=======
        if not self.settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — returning fallback stream.")
            yield "Groq API key is not configured.\n---JSON---\n" + json.dumps(fallback_report().model_dump())
            return

        if history is None:
            history = []

        messages = self._build_messages(user_text, face_emotion, history, text_emotion_summary)
>>>>>>> e0df7c7515413c00067c58471d916a2c19ab0679

        payload = {
            "model": self.settings.GROQ_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
            "stream": True,
<<<<<<< HEAD
            "options": {"temperature": 0.55, "top_p": 0.92, "num_ctx": 4096},
=======
>>>>>>> e0df7c7515413c00067c58471d916a2c19ab0679
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
