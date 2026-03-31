"""
orchestrator_status.py — Orchestrator Monitoring API Endpoints

Provides visibility into the dual-LLM orchestrator's state:
  - GET  /api/orchestrator/status  — Both providers' health, routing stats
  - GET  /api/orchestrator/logs    — Recent routing decisions
  - POST /api/orchestrator/refresh — Re-check provider health
"""
from __future__ import annotations

import logging
from fastapi import APIRouter

from app.services.llm_orchestrator import get_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])


@router.get("/status")
async def get_status():
    """Get current orchestrator status and statistics."""
    orchestrator = get_orchestrator()
    return orchestrator.get_status()


@router.get("/logs")
async def get_logs(limit: int = 20):
    """Get recent routing decisions."""
    orchestrator = get_orchestrator()
    stats = orchestrator.get_stats()
    decisions = stats.recent_decisions[-limit:] if stats.recent_decisions else []
    return {
        "decisions": [
            {
                "provider_used": d.provider_used,
                "task_type": d.task_type,
                "latency_ms": d.latency_ms,
                "fallback_used": d.fallback_used,
                "pii_scrubbed": d.pii_scrubbed,
                "error": d.error,
            }
            for d in reversed(decisions)
        ],
        "total_count": stats.total_requests,
    }


@router.post("/refresh")
async def refresh_health():
    """Re-check both providers' health status."""
    orchestrator = get_orchestrator()
    await orchestrator.refresh_health()
    return orchestrator.get_status()
