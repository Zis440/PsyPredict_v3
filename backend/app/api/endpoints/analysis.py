"""
analysis.py — PsyPredict Text Analysis & Health Endpoints (FastAPI)
Endpoints:
  POST /api/analyze/text  — standalone DistilBERT text emotion + crisis scoring
  GET  /api/health        — system health check (LLM provider, DistilBERT status)
  GET  /api/llm/status    — detailed LLM provider status
"""
from __future__ import annotations

import logging

from fastapi import APIRouter

from app.schemas import (
    HealthResponse,
    LLMStatusResponse,
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
    Returns status of the active LLM provider, model name, DistilBERT load status.
    """
    llm_ok = await ollama_engine.is_reachable()
    distilbert_ok = text_emotion_engine.is_loaded

    overall = "ok" if (llm_ok and distilbert_ok) else "degraded"

    if not llm_ok:
        logger.warning(
            "Health check: LLM provider '%s' unreachable (base_url=%s)",
            ollama_engine.provider_name,
            ollama_engine.base_url,
        )
    if not distilbert_ok:
        logger.warning("Health check: DistilBERT not loaded. Error: %s", text_emotion_engine.load_error)

    return HealthResponse(
        status=overall,
        llm_provider=ollama_engine.provider_name,
        llm_reachable=llm_ok,
        llm_model=ollama_engine.model_name,
        distilbert_loaded=distilbert_ok,
    )


# ---------------------------------------------------------------------------
# GET /api/llm/status — Detailed LLM provider status
# ---------------------------------------------------------------------------

@router.get("/llm/status", response_model=LLMStatusResponse)
async def llm_status():
    """
    Detailed LLM provider status.
    Reports which provider is active, whether it's reachable,
    the model being used, and whether a fallback provider is available.
    """
    reachable = await ollama_engine.is_reachable()

    # Check if fallback is available
    provider = ollama_engine.provider_name
    fallback_available = False

    if provider == "ollama" and settings.GROQ_API_KEY:
        # Ollama is primary but Groq key exists as potential fallback
        fallback_available = True
    elif provider == "groq":
        # Could potentially fall back to Ollama, but we can't check
        # without instantiating it — just report False
        fallback_available = False

    return LLMStatusResponse(
        provider=provider,
        reachable=reachable,
        model=ollama_engine.model_name,
        base_url=ollama_engine.base_url,
        fallback_available=fallback_available,
    )
