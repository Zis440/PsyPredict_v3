"""
remedies.py — PsyPredict Remedy Endpoint (FastAPI)
Preserved feature: CSV-based remedy lookup (remedy_engine.py unchanged).
Adapted from Flask Blueprint to FastAPI APIRouter with async wrapper.
"""
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas import RemedyResponse
from app.services.remedy_engine import remedy_engine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/get_advice", response_model=RemedyResponse)
async def get_advice(condition: str = Query(..., min_length=1, max_length=100)):
    """
    Lookup remedy by condition name (case-insensitive partial match).
    Preserved from original implementation — remedy_engine.py unchanged.
    Example: GET /api/get_advice?condition=Anxiety
    """
    # Strip and validate
    condition = condition.strip()
    if not condition:
        raise HTTPException(status_code=400, detail="Condition parameter cannot be empty")

    # Run sync CSV lookup in thread pool
    result = await asyncio.to_thread(remedy_engine.get_remedy, condition)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No remedy found for condition: '{condition}'",
        )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return RemedyResponse(**result)