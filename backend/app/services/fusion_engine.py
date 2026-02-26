"""
fusion_engine.py — PsyPredict Multimodal Weighted Fusion Engine
Combines text emotion score + face emotion score → final risk score.
Weights are configurable via app config (TEXT_WEIGHT, FACE_WEIGHT).
Speech modality placeholder included for future expansion.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Face emotion → distress score mapping
# Calibrated: fear/sadness = high distress, happy = minimal distress
# ---------------------------------------------------------------------------

FACE_DISTRESS_SCORES: dict[str, float] = {
    "fear": 0.80,
    "sad": 0.70,
    "angry": 0.50,
    "disgust": 0.40,
    "surprised": 0.30,
    "neutral": 0.20,
    "happy": 0.05,
}

# DistilBERT emotion labels → distress scores
TEXT_EMOTION_DISTRESS_SCORES: dict[str, float] = {
    "sadness": 0.85,
    "fear": 0.80,
    "anger": 0.60,
    "disgust": 0.50,
    "surprise": 0.30,
    "joy": 0.05,
    "love": 0.05,
    "neutral": 0.20,
}


@dataclass
class FusionResult:
    """Result of multimodal fusion scoring."""
    final_risk_score: float        # 0.0–1.0 weighted combined score
    text_score: float              # Raw text distress score
    face_score: float              # Raw face distress score
    speech_score: Optional[float]  # Placeholder — always None for now
    dominant_modality: str         # "text" | "face" | "balanced"
    text_weight: float
    face_weight: float


class FusionEngine:
    """
    Computes the weighted multimodal risk score.

    Formula:
        final_risk_score = (TEXT_WEIGHT * text_distress) + (FACE_WEIGHT * face_distress)

    Weights are loaded from app config at runtime.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def _text_distress(self, dominant_text_emotion: str) -> float:
        """Map dominant text emotion label → distress score."""
        return TEXT_EMOTION_DISTRESS_SCORES.get(
            dominant_text_emotion.lower(), 0.20
        )

    def _face_distress(self, face_emotion: str) -> float:
        """Map face emotion label → distress score."""
        return FACE_DISTRESS_SCORES.get(face_emotion.lower(), 0.20)

    def compute(
        self,
        dominant_text_emotion: str,
        face_emotion: str,
        speech_score: Optional[float] = None,  # Future: speech sentiment
    ) -> FusionResult:
        """
        Compute weighted fusion score from available modalities.

        Args:
            dominant_text_emotion: Top emotion from DistilBERT (e.g. "sadness")
            face_emotion: Detected face emotion from Keras CNN (e.g. "sad")
            speech_score: Optional speech distress score (0.0–1.0)

        Returns:
            FusionResult with final weighted score and per-modality breakdown
        """
        tw = self.settings.TEXT_WEIGHT
        fw = self.settings.FACE_WEIGHT

        text_score = self._text_distress(dominant_text_emotion)
        face_score = self._face_distress(face_emotion)

        # If speech is provided in future, re-normalize weights
        if speech_score is not None:
            speech_weight = 1.0 - tw - fw
            if speech_weight > 0:
                final = (tw * text_score) + (fw * face_score) + (speech_weight * speech_score)
            else:
                final = (tw * text_score) + (fw * face_score)
        else:
            # Normalize text + face weights to sum to 1.0
            total = tw + fw
            final = ((tw / total) * text_score) + ((fw / total) * face_score)

        final = round(min(max(final, 0.0), 1.0), 4)

        # Determine dominant modality
        if abs(text_score - face_score) < 0.10:
            dominant = "balanced"
        elif text_score > face_score:
            dominant = "text"
        else:
            dominant = "face"

        logger.debug(
            "Fusion: text_emotion=%s(%.2f) face_emotion=%s(%.2f) → final=%.4f dominant=%s",
            dominant_text_emotion, text_score,
            face_emotion, face_score,
            final, dominant,
        )

        return FusionResult(
            final_risk_score=final,
            text_score=text_score,
            face_score=face_score,
            speech_score=speech_score,
            dominant_modality=dominant,
            text_weight=tw,
            face_weight=fw,
        )


# Singleton
fusion_engine = FusionEngine()
