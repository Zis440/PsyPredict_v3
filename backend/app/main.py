"""
main.py — PsyPredict FastAPI Application (Production v1.4)
Key features:
  - Dual-LLM orchestration (Ollama local + Groq cloud)
  - FAISS-powered semantic knowledge retrieval
  - Patient memory with adaptive preferences
  - Async request handling (FastAPI + Uvicorn)
  - CORS middleware + Rate limiting (SlowAPI)
  - Structured logging (Python logging)
  - Startup model pre-warming + orchestrator initialization
  - Graceful shutdown (both LLM clients cleanup)
  - FastAPI auto docs at /docs (Swagger) and /redoc
"""
from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.api.endpoints.facial import router as facial_router
from app.api.endpoints.remedies import router as remedies_router
from app.api.endpoints.therapist import router as therapist_router
from app.api.endpoints.analysis import router as analysis_router
from app.api.endpoints.progress import router as progress_router
from app.api.endpoints.orchestrator_status import router as orchestrator_router
from app.api.endpoints.mind_model import router as mind_model_router
from app.api.endpoints.visual_psychology import router as visual_router
from app.api.endpoints.assessment_engine import router as assessment_router
from app.api.endpoints.reports import router as reports_router

settings = get_settings()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown events)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup:
      1. Initialize dual-LLM orchestrator (Ollama + Groq health checks)
      2. Pre-warm ML models (DistilBERT + Crisis classifier) in background
      3. Build FAISS knowledge index in background
      4. Initialize patient memory engine
    Shutdown:
      Close both LLM clients gracefully.
    """
    logger.info("═══════════════════════════════════════════════")
    logger.info("[BOOT] PsyPredict v1.4 -- Emotionally Intelligent AI")
    logger.info("═══════════════════════════════════════════════")

    import asyncio as _asyncio

    # ── 1. Initialize Dual-LLM Orchestrator ──────────────────────────────────
    if settings.LLM_ORCHESTRATOR_ENABLED:
        logger.info("Initializing dual-LLM orchestrator...")
        from app.services.ollama_engine import orchestrator
        await orchestrator.initialize()
        logger.info(
            "Orchestrator status: local=%s, cloud=%s",
            "YES" if orchestrator._local_available else "NO",
            "YES" if orchestrator._cloud_available else "NO",
        )
    else:
        # Fallback: use single provider (backward compat)
        from app.services.ollama_engine import ollama_engine
        logger.info(
            "LLM Provider (single): %s (model=%s, base_url=%s)",
            ollama_engine.provider_name,
            ollama_engine.model_name,
            ollama_engine.base_url,
        )
        reachable = await ollama_engine.is_reachable()
        if reachable:
            logger.info("[OK] %s reachable", ollama_engine.provider_name.upper())
        else:
            logger.warning("[WARN] %s NOT reachable", ollama_engine.provider_name.upper())

    # ── 2. Pre-warm ML Models (safe sequential background task) ──────────────
    async def _safe_prewarm_models():
        try:
            logger.info("Initializing DistilBERT text emotion model (background)...")
            from app.services.text_emotion_engine import initialize as init_text
            await _asyncio.to_thread(init_text, settings.DISTILBERT_MODEL)

            logger.info("Initializing crisis detection classifier (background)...")
            from app.services.crisis_engine import initialize_crisis_classifier
            await _asyncio.to_thread(initialize_crisis_classifier)

            if settings.KNOWLEDGE_INDEX_ENABLED:
                logger.info("Building FAISS knowledge index (background)...")
                from app.services.knowledge_index import get_knowledge_index
                ki = get_knowledge_index()
                await _asyncio.to_thread(ki.build)
        except Exception as exc:
            logger.warning("Background pre-warming notice: %s", exc)

    _asyncio.create_task(_safe_prewarm_models())

    # ── 4. Initialize Patient Memory ─────────────────────────────────────────
    logger.info("Initializing patient memory engine...")
    from app.services.patient_memory import init_patient_memory
    init_patient_memory(
        backend=settings.PATIENT_MEMORY_BACKEND,
        sqlite_path=settings.SQLITE_DB_PATH,
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_KEY,
        max_sessions=settings.PATIENT_HISTORY_MAX_SESSIONS,
    )
    logger.info("[OK] Patient memory initialized (%s)", settings.PATIENT_MEMORY_BACKEND)

    logger.info("═══════════════════════════════════════════════")
    logger.info("[OK] Startup complete. Listening on port 7860.")
    logger.info("   Docs:         http://localhost:7860/docs")
    logger.info("   Orchestrator: http://localhost:7860/api/orchestrator/status")
    logger.info("═══════════════════════════════════════════════")

    yield  # ── Application Running ──

    logger.info("Shutting down PsyPredict backend...")
    if settings.LLM_ORCHESTRATOR_ENABLED:
        from app.services.ollama_engine import orchestrator as orch
        await orch.close()
    else:
        from app.services.ollama_engine import ollama_engine as engine
        await engine.close()
    logger.info("Goodbye.")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="PsyPredict API",
        description=(
            "Production-grade emotionally intelligent mental health AI system. "
            "Dual-LLM orchestration (Ollama + Groq) with FAISS semantic search, "
            "adaptive patient memory, and Bhagavad Gita wisdom integration."
        ),
        version="1.4.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── Rate Limiter ─────────────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── CORS ────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],          # Tighten to specific origin in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global Exception Handler ─────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception: %s | path=%s", exc, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again."},
        )

    # ── Routers ──────────────────────────────────────────────────────────────
    app.include_router(facial_router, prefix="/api", tags=["Facial Emotion"])
    app.include_router(remedies_router, prefix="/api", tags=["Remedies"])
    app.include_router(therapist_router, prefix="/api", tags=["AI Therapist"])
    app.include_router(analysis_router, prefix="/api", tags=["Text Analysis & Health"])
    app.include_router(progress_router, tags=["Patient Progress"])
    app.include_router(orchestrator_router, tags=["Orchestrator"])
    app.include_router(mind_model_router, prefix="/api", tags=["Mind Model & Memory Analytics"])
    app.include_router(visual_router, prefix="/api/visual", tags=["Visual Psychology"])
    app.include_router(assessment_router, prefix="/api/assessments", tags=["Assessments"])
    app.include_router(reports_router, prefix="/api/reports", tags=["Master Reports"])

    # ── Keep-Alive ping (no model deps) ──────────────────────────────────────
    import time as _time

    @app.get("/ping", tags=["Health"])
    async def ping():
        return {"status": "alive", "timestamp": _time.time()}

    return app


app = create_app()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
        log_level=settings.LOG_LEVEL.lower(),
        workers=1,  # Keep at 1: models are singletons loaded in memory
    )

