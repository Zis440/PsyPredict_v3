"""
progress.py — Patient Progress & Preferences API Endpoints

Endpoints for:
  - GET  /api/patient/{user_id}/progress     — Progress timeline, emotion trends, risk trajectory
  - GET  /api/patient/{user_id}/preferences  — Current patient preferences
  - PUT  /api/patient/{user_id}/preferences  — Update preferences
  - POST /api/patient/{user_id}/feedback     — Submit session feedback
  - POST /api/patient/{user_id}/snapshot     — Generate progress snapshot on demand
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException

from app.schemas import (
    PatientPreferences,
    PatientPreferencesUpdate,
    PatientProgressResponse,
    SessionFeedback,
)
from app.services.patient_memory import get_patient_memory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/patient", tags=["patient"])


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

@router.get("/{user_id}/progress")
async def get_progress(user_id: str):
    """Get patient progress data for the dashboard."""
    memory = get_patient_memory()
    progress = memory.get_progress(user_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="No progress data found for this patient.")
    return progress


@router.post("/{user_id}/snapshot")
async def generate_snapshot(user_id: str):
    """Generate a progress snapshot on demand."""
    from app.services.progress_tracker import generate_and_save_snapshot
    success = await generate_and_save_snapshot(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Unable to generate snapshot. No session data found.")
    return {"status": "ok", "message": "Progress snapshot generated."}


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------

@router.get("/{user_id}/preferences")
async def get_preferences(user_id: str):
    """Get patient preferences."""
    memory = get_patient_memory()
    prefs = memory.get_preferences(user_id)
    if prefs is None:
        # Return defaults
        return PatientPreferences(user_id=user_id).model_dump()
    return prefs


@router.put("/{user_id}/preferences")
async def update_preferences(user_id: str, update: PatientPreferencesUpdate):
    """Update patient preferences."""
    memory = get_patient_memory()
    success = memory.update_preferences(
        user_id=user_id,
        preferred_tone=update.preferred_tone,
        verbosity=update.verbosity,
        framework_preference=update.framework_preference,
        topics_to_avoid=update.topics_to_avoid,
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update preferences.")
    return {"status": "ok", "message": "Preferences updated."}


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

@router.post("/{user_id}/feedback")
async def submit_feedback(user_id: str, feedback: SessionFeedback):
    """Submit session feedback."""
    memory = get_patient_memory()
    success = memory.save_feedback(
        user_id=user_id,
        rating=feedback.rating,
        message_id=feedback.message_id,
        comment=feedback.comment,
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save feedback.")
    return {"status": "ok", "message": "Feedback recorded."}
