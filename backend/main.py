"""
main.py — PsyPredict FastAPI Application (Root entry point)
Delegates to app.main for the actual application factory.
Key features:
  - Async request handling (FastAPI + Uvicorn)
  - CORS middleware
  - Rate limiting (SlowAPI)
  - Structured logging (Python logging)
  - Startup model pre-warming
  - Graceful shutdown (LLM client cleanup)
  - FastAPI auto docs at /docs (Swagger) and /redoc
"""
from __future__ import annotations

import asyncio
import sys

# ---------------------------------------------------------------------------
# Windows asyncio fix — prevents noisy "ConnectionResetError: [WinError 10054]"
# when a streaming client disconnects before the response finishes.
# SelectorEventLoop handles abrupt pipe closures gracefully unlike the default
# ProactorEventLoop on Windows.
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import the app from the package — this is the canonical entry point
from app.main import app  # noqa: E402, F401
from app.config import get_settings  # noqa: E402

settings = get_settings()

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
