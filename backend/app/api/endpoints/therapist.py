"""
therapist.py — PsyPredict AI Therapist Endpoint (FastAPI)
Full inference pipeline:
  1. Input sanitization + validation (Pydantic)
  2. Text emotion classification (DistilBERT)
  3. Crisis evaluation (zero-shot NLI) — override if triggered
  4. Multimodal fusion (text + face)
  5. Patient memory retrieval (adaptive learning)
  6. Gita shloka context injection from CSV corpus
  7. Ollama/LLaMA 3 structured report generation
  8. PsychReport JSON schema validation
  9. Session save for adaptive learning
  10. Streaming response option
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
from app.services.patient_memory import get_patient_memory

logger = logging.getLogger(__name__)

router = APIRouter()

# Map risk levels to CSV conditions — enriched for diversity
RISK_TO_CONDITION: dict[str, str] = {
    "critical": "Suicidal Ideation",
    "high": "Depression",
    "moderate": "Anxiety",
    "low": "Stress",
    "minimal": "Stress",
}

# Map emotions to CSV conditions — enriched and more accurate
EMOTION_TO_CONDITION: dict[str, str] = {
    "sad": "Depression",
    "sadness": "Depression",
    "fear": "Anxiety",
    "angry": "Anger Management",
    "anger": "Anger Management",
    "disgust": "OCD",
    "surprised": "Panic Disorder",
    "surprise": "Panic Disorder",
    "neutral": "Stress",
    "happy": "Stress",
    "joy": "Stress",
    "love": "Stress",
}


# ---------------------------------------------------------------------------
# POST /api/chat
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):  # type: ignore[misc]
    """
    Main inference endpoint.
    Accepts user message + webcam emotion + history + user_id.
    Returns structured PsychReport + conversational reply + CSV remedy data.
    Patient memory provides adaptive learning across sessions.
    """
    user_text = req.message
    face_emotion = req.emotion or "neutral"
    history = req.history
    user_id = req.user_id  # For patient memory (adaptive learning)

    # ── Step 1: Text Emotion Classification ────────────────────────────────
    text_labels = await text_emotion_engine.classify(user_text)
    dominant_text_emotion = text_labels[0].label if text_labels else "neutral"
    text_emotion_summary = text_emotion_engine.summary_string(text_labels)

    logger.info(
        "Text emotion: %s | Face emotion: %s | User: %s",
        text_emotion_summary,
        face_emotion,
        user_id or "anonymous",
    )

    # ── Step 2: Crisis Evaluation (OVERRIDE LAYER) ──────────────────────────
    crisis_score, crisis_triggered = await crisis_engine.evaluate(user_text)

    if crisis_triggered:
        reply, report = crisis_engine.build_crisis_report(crisis_score)
        remedy_data = remedy_engine.get_remedy("Suicidal Ideation") or remedy_engine.get_remedy("Anxiety")
        remedy = RemedyResponse(**remedy_data) if remedy_data and "error" not in remedy_data else None

        # Save crisis session to patient memory
        if user_id:
            try:
                mem = get_patient_memory()
                mem.save_session(
                    user_id=user_id,
                    dominant_emotion="crisis",
                    risk_level="CRITICAL",
                    fusion_score=float(crisis_score),
                    cognitive_distortions=["Hopelessness", "All-or-nothing thinking"],
                    interventions=["Crisis line referral"],
                    summary="Crisis triggered — immediate support provided",
                    user_message=user_text[:200],
                )
            except Exception as e:
                logger.warning("Failed to save crisis session to memory: %s", e)

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

    # ── Step 4: Patient Memory Retrieval (Adaptive Learning) ─────────────────
    patient_profile = None
    if user_id:
        try:
            mem = get_patient_memory()
            patient_profile = mem.get_patient_profile(user_id)
            if patient_profile:
                logger.info("Patient profile loaded for user %s (%d chars)", user_id, len(patient_profile))
        except Exception as e:
            logger.warning("Patient memory retrieval failed: %s", e)

    # ── Step 5: Remedy / Gita Shloka Lookup (for LLM context) ──────────────
    # Priority: risk level → dominant text emotion → face emotion
    risk_key = ""  # Will be set after LLM generation for pre-lookup; use emotion for now
    condition = EMOTION_TO_CONDITION.get(dominant_text_emotion.lower(), "Anxiety")
    remedy_raw = remedy_engine.get_remedy(condition)
    gita_context = None
    remedy = None
    if remedy_raw and "error" not in remedy_raw:
        try:
            remedy = RemedyResponse(**remedy_raw)
            # Extract Gita shloka for LLM context injection
            gita_context = remedy_raw.get("gita_remedy", "")
            if gita_context:
                gita_context = f"Condition: {remedy_raw.get('condition', condition)}\nGita Wisdom: {gita_context}"
        except Exception as e:
            logger.warning("Could not build RemedyResponse: %s", e)

    # ── Step 6: Streaming Response ───────────────────────────────────────────
    if req.stream:
        async def stream_generator():
            accumulated = ""
            async for token in ollama_engine.generate_stream(
                user_text=user_text,
                face_emotion=face_emotion,
                history=history,
                text_emotion_summary=text_emotion_summary,
                patient_profile=patient_profile,
                gita_context=gita_context,
            ):
                accumulated += token
                yield token

        return StreamingResponse(stream_generator(), media_type="text/plain")

    # ── Step 7: LLM Generation (non-streaming) ──────────────────────────────
    reply, report = await ollama_engine.generate(
        user_text=user_text,
        face_emotion=face_emotion,
        history=history,
        text_emotion_summary=text_emotion_summary,
        patient_profile=patient_profile,
        gita_context=gita_context,
    )

    # ── Step 8: Save Session to Patient Memory (Adaptive Learning) ──────────
    if user_id:
        try:
            mem = get_patient_memory()
            mem.save_session(
                user_id=user_id,
                dominant_emotion=dominant_text_emotion,
                risk_level=report.risk_classification.value,
                fusion_score=float(fusion.final_risk_score),
                cognitive_distortions=report.cognitive_distortions,
                interventions=report.suggested_interventions,
                summary=report.emotional_state_summary,
                user_message=user_text[:200],
            )
        except Exception as e:
            logger.warning("Failed to save session to patient memory: %s", e)

    return ChatResponse(
        response=reply,
        report=report,
        text_emotion=text_labels,
        fusion_risk_score=float(fusion.final_risk_score),
        remedy=remedy,
    )
