"""
main.py — PsyPredict FastAPI Application (Production)
Replaces Flask. Key features:
  - Async request handling (FastAPI + Uvicorn)
  - CORS middleware
  - Rate limiting (SlowAPI)
  - Structured logging (Python logging)
  - Startup model pre-warming
  - Graceful shutdown (Ollama client cleanup)
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
    Startup: pre-warm models (DistilBERT + Crisis classifier).
    Shutdown: close Ollama async client.
    """
    logger.info("═══════════════════════════════════════")
    logger.info("🚀 PsyPredict v2.0 — Production Backend")
    logger.info("═══════════════════════════════════════")
    logger.info("Config: Ollama=%s model=%s", settings.OLLAMA_BASE_URL, settings.OLLAMA_MODEL)

    # Pre-warm DistilBERT text emotion model
    logger.info("Pre-warming DistilBERT text emotion model...")
    from app.services.text_emotion_engine import initialize as init_text
    init_text(settings.DISTILBERT_MODEL)

    # Pre-warm Crisis zero-shot classifier
    logger.info("Pre-warming crisis detection classifier...")
    from app.services.crisis_engine import initialize_crisis_classifier
    initialize_crisis_classifier()

    # Check Ollama availability (non-blocking warn only)
    from app.services.ollama_engine import ollama_engine
    reachable = await ollama_engine.is_reachable()
    if reachable:
        logger.info("✅ Ollama reachable at %s (model: %s)", settings.OLLAMA_BASE_URL, settings.OLLAMA_MODEL)
    else:
        logger.warning(
            "⚠️  Ollama NOT reachable at %s — chat will return fallback responses. "
            "Run: ollama serve && ollama pull %s",
            settings.OLLAMA_BASE_URL,
            settings.OLLAMA_MODEL,
        )

    logger.info("✅ Startup complete. Listening on port 7860.")
    logger.info("   Docs: http://localhost:7860/docs")
    logger.info("═══════════════════════════════════════")

    yield  # ── Application Running ──

    logger.info("Shutting down PsyPredict backend...")
    await ollama_engine.close()
    logger.info("Goodbye.")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="PsyPredict API",
        description=(
            "Production-grade multimodal mental health AI system. "
            "Powered by LLaMA 3 (Ollama) + DistilBERT + Keras CNN facial emotion model."
        ),
        version="2.0.0",
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
