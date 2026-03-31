"""
session_summarizer.py — Background Session Summarization

After each chat interaction, generates a 2-3 sentence summary of the
session using the local LLM (privacy-first: never sends full
conversations to the cloud).

Runs as a non-blocking background task so it doesn't affect response latency.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Summary generation prompt
_SUMMARY_PROMPT = """Summarize the following therapy session interaction in 2-3 concise sentences.
Focus on: the patient's main concern, emotional state, and any key insights or interventions.
Do NOT include any PII or names. Keep it clinical and professional.

Patient said: "{user_message}"

Therapist responded with risk level: {risk_level}, dominant emotion detected: {emotion}.
Cognitive distortions identified: {distortions}.

Summary:"""


async def generate_session_summary(
    user_message: str,
    risk_level: str = "MINIMAL",
    emotion: str = "neutral",
    distortions: Optional[list] = None,
) -> Optional[str]:
    """
    Generate a 2-3 sentence session summary using the local LLM.

    Uses Ollama (local) for privacy. Falls back to a template-based
    summary if LLM is unavailable.
    """
    try:
        from app.services.llm_orchestrator import get_orchestrator

        orchestrator = get_orchestrator()

        # Only use local LLM for privacy
        if not orchestrator._local_available or not orchestrator._local:
            return _template_summary(user_message, risk_level, emotion, distortions)

        prompt = _SUMMARY_PROMPT.format(
            user_message=user_message[:500],  # Truncate for safety
            risk_level=risk_level,
            emotion=emotion,
            distortions=", ".join(distortions or []) or "none identified",
        )

        # Use the local client directly (skip orchestration for this internal task)
        messages = [
            {"role": "system", "content": "You are a clinical note summarizer. Be concise and professional."},
            {"role": "user", "content": prompt},
        ]

        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{orchestrator._local.base_url}/api/chat",
                json={
                    "model": orchestrator._local.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 150},
                },
            )
            if response.status_code == 200:
                data = response.json()
                summary = data.get("message", {}).get("content", "").strip()
                if summary and len(summary) > 10:
                    return summary[:500]  # Cap length

        return _template_summary(user_message, risk_level, emotion, distortions)

    except Exception as exc:
        logger.debug("Session summary generation failed (expected if no local LLM): %s", exc)
        return _template_summary(user_message, risk_level, emotion, distortions)


def _template_summary(
    user_message: str,
    risk_level: str,
    emotion: str,
    distortions: Optional[list],
) -> str:
    """Fallback template-based summary when LLM is unavailable."""
    msg_preview = user_message[:100].strip()
    distortion_text = ", ".join(distortions[:3]) if distortions else "none"
    return (
        f"Patient expressed '{emotion}' emotional state (risk: {risk_level}). "
        f"Topic: \"{msg_preview}...\" "
        f"Cognitive patterns: {distortion_text}."
    )


async def summarize_and_save(
    user_id: str,
    user_message: str,
    risk_level: str = "MINIMAL",
    emotion: str = "neutral",
    distortions: Optional[list] = None,
) -> None:
    """
    Background task: generate a summary and update the latest session record.
    This is fire-and-forget — errors are logged but don't affect the user.
    """
    try:
        summary = await generate_session_summary(
            user_message, risk_level, emotion, distortions
        )
        if summary and user_id:
            from app.services.patient_memory import get_patient_memory
            memory = get_patient_memory()

            if memory.backend == "sqlite":
                import sqlite3
                conn = memory._get_conn()
                try:
                    # Update the most recent session for this user
                    conn.execute(
                        """UPDATE sessions SET summary = ?
                           WHERE user_id = ? AND id = (
                               SELECT id FROM sessions WHERE user_id = ?
                               ORDER BY created_at DESC LIMIT 1
                           )""",
                        (summary, user_id, user_id),
                    )
                    conn.commit()
                except Exception as exc:
                    logger.error("Failed to save session summary: %s", exc)
                finally:
                    conn.close()

        logger.debug("Session summary saved for user %s", user_id)
    except Exception as exc:
        logger.error("Background summarization failed: %s", exc)
