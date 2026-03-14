"""
therapist.py — PsyPredict AI Therapist Endpoint (FastAPI)
Full inference pipeline:
  1. Input sanitization + validation (Pydantic)
  2. Text emotion classification (DistilBERT)
  3. Crisis evaluation (zero-shot NLI) — override if triggered
  4. Multimodal fusion (text + face)
  5. Ollama/Llama3 structured report generation
  6. PsychReport JSON schema validation
  7. Streaming response option
"""
from __future__ import annotations

import logging
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest, ChatResponse, PsychReport, RemedyResponse
from app.services.ollama_engine import ollama_engine
from app.services.text_emotion_engine import text_emotion_engine
from app.services.crisis_engine import crisis_engine
from app.services.fusion_engine import fusion_engine
from app.services.remedy_engine import remedy_engine

logger = logging.getLogger(__name__)

router = APIRouter()

# Map risk levels / dominant emotions to CSV conditions
RISK_TO_CONDITION: dict[str, str] = {
    "critical": "Suicidal Ideation",
    "high": "Depression",
    "moderate": "Anxiety",
    "low": "Anxiety",
    "minimal": "Anxiety",
}

EMOTION_TO_CONDITION: dict[str, str] = {
    "sad": "Depression",
    "fear": "Anxiety",
    "angry": "Bipolar Disorder",
    "disgust": "Anxiety",
    "surprised": "Anxiety",
    "neutral": "Anxiety",
    "happy": "Anxiety",
}


# ---------------------------------------------------------------------------
# POST /api/chat
# ---------------------------------------------------------------------------

@router.post("/chat")
async def chat(req: ChatRequest):  # type: ignore[misc]
    """
    Main inference endpoint.
    Accepts user message + webcam emotion + history.
    Returns structured PsychReport + conversational reply + CSV remedy data.
    """
    user_text = req.message
    face_emotion = req.emotion or "neutral"
    history = req.history

    # ── Step 1: Text Emotion Classification ────────────────────────────────
    text_labels = await text_emotion_engine.classify(user_text)
    dominant_text_emotion = text_labels[0].label if text_labels else "neutral"
    text_emotion_summary = text_emotion_engine.summary_string(text_labels)

    logger.info(
        "Text emotion: %s | Face emotion: %s",
        text_emotion_summary,
        face_emotion,
    )

    # ── Step 2: Crisis Evaluation (OVERRIDE LAYER) ──────────────────────────
    crisis_score, crisis_triggered = await crisis_engine.evaluate(user_text)

    if crisis_triggered:
        reply, report = crisis_engine.build_crisis_report(crisis_score)
        remedy_data = remedy_engine.get_remedy("Suicidal Ideation") or remedy_engine.get_remedy("Anxiety")
        remedy = RemedyResponse(**remedy_data) if remedy_data and "error" not in remedy_data else None
        return ChatResponse(
            response=reply,
            report=report,
            text_emotion=text_labels,
            fusion_risk_score=float(crisis_score),
            remedy=remedy,
        )

    # ── Step 3: Multimodal Fusion ────────────────────────────────────────────
    fusion = fusion_engine.compute(
        dominant_text_emotion=dominant_text_emotion,
        face_emotion=face_emotion,
    )
    logger.info("Fusion risk score: %.4f (dominant: %s)", fusion.final_risk_score, fusion.dominant_modality)

    # ── Step 4: Streaming Response ───────────────────────────────────────────
    if req.stream:
        async def stream_generator():
            async for token in ollama_engine.generate_stream(
                user_text=user_text,
                face_emotion=face_emotion,
                history=history,
                text_emotion_summary=text_emotion_summary,
            ):
                yield token

        return StreamingResponse(stream_generator(), media_type="text/plain")

    # ── Step 5: LLM Generation (non-streaming) ──────────────────────────────
    reply, report = await ollama_engine.generate(
        user_text=user_text,
        face_emotion=face_emotion,
        history=history,
        text_emotion_summary=text_emotion_summary,
    )

    # ── Step 6: Remedy Lookup from CSV ──────────────────────────────────────
    # Priority: risk level → dominant text emotion → face emotion
    risk_key = report.risk_classification.value.lower()
    condition = RISK_TO_CONDITION.get(risk_key) or EMOTION_TO_CONDITION.get(dominant_text_emotion.lower(), "Anxiety")
    remedy_raw = remedy_engine.get_remedy(condition)
    remedy = None
    if remedy_raw and "error" not in remedy_raw:
        try:
            remedy = RemedyResponse(**remedy_raw)
        except Exception as e:
            logger.warning("Could not build RemedyResponse: %s", e)

    return ChatResponse(
        response=reply,
        report=report,
        text_emotion=text_labels,
        fusion_risk_score=float(fusion.final_risk_score),
        remedy=remedy,
    )
