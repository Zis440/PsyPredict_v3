"""
analysis.py — PsyPredict Text Analysis & Health Endpoints (FastAPI)
New endpoints:
  POST /api/analyze/text  — standalone DistilBERT text emotion + crisis scoring
  GET  /api/health        — system health check (Ollama, DistilBERT status)
"""
from __future__ import annotations

import logging

from fastapi import APIRouter

from app.schemas import (
    HealthResponse,
    TextAnalysisRequest,
    TextAnalysisResponse,
)
from app.services.crisis_engine import crisis_engine
from app.services.ollama_engine import ollama_engine
from app.services.text_emotion_engine import text_emotion_engine
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

settings = get_settings()


# ---------------------------------------------------------------------------
# POST /api/analyze/text
# ---------------------------------------------------------------------------

@router.post("/analyze/text", response_model=TextAnalysisResponse)
async def analyze_text(req: TextAnalysisRequest):
    """
    Standalone text emotion analysis pipeline (no LLM, no history needed).
    Returns multi-label emotion scores + crisis risk score.
    Useful for lightweight pre-screening before full chat inference.
    """
    # Text emotion classification
    labels = await text_emotion_engine.classify(req.text)
    dominant = labels[0].label if labels else "neutral"

    # Crisis risk scoring
    crisis_score, crisis_triggered = await crisis_engine.evaluate(req.text)

    return TextAnalysisResponse(
        emotions=labels,
        dominant=dominant,
        crisis_risk=round(float(crisis_score), 4),
        crisis_triggered=crisis_triggered,
    )


# ---------------------------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse)
async def health():
    """
    System health check.
    Returns status of Ollama (reachable?), model name, DistilBERT load status.
    """
    ollama_ok = await ollama_engine.is_reachable()
    distilbert_ok = text_emotion_engine.is_loaded

    overall = "ok" if (ollama_ok and distilbert_ok) else "degraded"

    if not ollama_ok:
        logger.warning("Health check: Ollama unreachable at %s", settings.OLLAMA_BASE_URL)
    if not distilbert_ok:
        logger.warning("Health check: DistilBERT not loaded. Error: %s", text_emotion_engine.load_error)

    return HealthResponse(
        status=overall,
        ollama_reachable=ollama_ok,
        ollama_model=settings.OLLAMA_MODEL,
        distilbert_loaded=distilbert_ok,
    )
