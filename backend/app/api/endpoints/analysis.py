"""
analysis.py — PsyPredict Text Analysis & Health Endpoints (FastAPI) v1.4
Endpoints:
  POST /api/analyze/text  — standalone DistilBERT text emotion + crisis scoring
  GET  /api/health        — system health check (LLM providers, DistilBERT, knowledge index)
  GET  /api/llm/status    — detailed LLM provider status (orchestrator-aware)
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

@router.get("/health")
async def health():
    """
    System health check.
    When orchestrator is enabled, reports both LLM providers.
    Also reports DistilBERT and knowledge index status.
    """
    distilbert_ok = text_emotion_engine.is_loaded

    # Check knowledge index status
    knowledge_index_ready = False
    if settings.KNOWLEDGE_INDEX_ENABLED:
        try:
            from app.services.knowledge_index import get_knowledge_index
            ki = get_knowledge_index()
            knowledge_index_ready = ki.is_ready
        except Exception:
            pass

    if settings.LLM_ORCHESTRATOR_ENABLED:
        from app.services.ollama_engine import orchestrator
        any_reachable = orchestrator._local_available or orchestrator._cloud_available
        overall = "ok" if (any_reachable and distilbert_ok) else "degraded"

        return {
            "status": overall,
            "version": "1.4.0",
            "orchestrator_enabled": True,
            "llm_local": {
                "provider": "ollama",
                "reachable": orchestrator._local_available,
                "model": orchestrator._local.model_name if orchestrator._local else "N/A",
            },
            "llm_cloud": {
                "provider": "groq",
                "reachable": orchestrator._cloud_available,
                "model": orchestrator._cloud.model_name if orchestrator._cloud else "N/A",
            },
            "distilbert_loaded": distilbert_ok,
            "knowledge_index_ready": knowledge_index_ready,
        }
    else:
        llm_ok = await ollama_engine.is_reachable()
        overall = "ok" if (llm_ok and distilbert_ok) else "degraded"

        return HealthResponse(
            status=overall,
            llm_provider=ollama_engine.provider_name,
            llm_reachable=llm_ok,
            llm_model=ollama_engine.model_name,
            distilbert_loaded=distilbert_ok,
            version="1.4.0",
        )


# ---------------------------------------------------------------------------
# GET /api/llm/status — Detailed LLM provider status
# ---------------------------------------------------------------------------

@router.get("/llm/status")
async def llm_status():
    """
    Detailed LLM provider status.
    When orchestrator is enabled, reports both providers with routing stats.
    """
    if settings.LLM_ORCHESTRATOR_ENABLED:
        from app.services.ollama_engine import orchestrator
        return orchestrator.get_status()

    reachable = await ollama_engine.is_reachable()
    provider = ollama_engine.provider_name
    fallback_available = False

    if provider == "ollama" and settings.GROQ_API_KEY:
        fallback_available = True

    return LLMStatusResponse(
        provider=provider,
        reachable=reachable,
        model=ollama_engine.model_name,
        base_url=ollama_engine.base_url,
        fallback_available=fallback_available,
    )

