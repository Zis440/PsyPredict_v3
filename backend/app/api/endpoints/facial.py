"""
facial.py — PsyPredict Facial Emotion Detection Endpoint (FastAPI)
Preserved feature: Keras CNN face emotion model (emotion_engine.py unchanged).
Adapted from Flask Blueprint to FastAPI APIRouter with async file handling.
"""
from __future__ import annotations

import logging

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.schemas import EmotionResponse
from app.services.emotion_engine import emotion_detector

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict/emotion", response_model=EmotionResponse)
async def predict_emotion(file: UploadFile = File(...)):
    """
    Receives an image file and returns detected face emotion + confidence.
    Preserved from original implementation — Keras CNN model unchanged.
    Gracefully handles empty/corrupt webcam frames without crashing.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Accepted: JPEG, PNG, WEBP",
        )

    try:
        contents = await file.read()

        # Guard: empty frame (webcam not ready yet) — return neutral silently
        if not contents or len(contents) < 100:
            return EmotionResponse(emotion="neutral", confidence=0.0, message="Empty frame skipped")

        if len(contents) > 10 * 1024 * 1024:  # 10 MB limit
            raise HTTPException(status_code=413, detail="Image too large (max 10MB)")

        # Decode to OpenCV format in memory (no disk I/O)
        file_bytes = np.frombuffer(contents, np.uint8)

        if file_bytes.size == 0:
            return EmotionResponse(emotion="neutral", confidence=0.0, message="Empty buffer")

        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Guard: corrupted/blank frame — return neutral instead of crashing
        if image is None:
            return EmotionResponse(emotion="neutral", confidence=0.0, message="Camera frame not ready")

        result = emotion_detector.detect_emotion(image)

        if "error" in result:
            # No face detected — return neutral without crashing
            return EmotionResponse(emotion="neutral", confidence=0.0, message=result.get("error"))

        return EmotionResponse(**result)

    except HTTPException:
        raise
    except Exception as exc:
        # Log at DEBUG level to reduce terminal noise during normal webcam polling
        logger.debug("Facial emotion prediction skipped: %s", exc)
        return EmotionResponse(emotion="neutral", confidence=0.0, message="Frame processing error")