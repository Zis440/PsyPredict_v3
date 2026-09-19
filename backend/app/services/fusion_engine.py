"""
fusion_engine.py — PsyPredict Multimodal Weighted Fusion Engine
Combines text emotion score + face emotion score + oculomotor/biometric telemetry → final risk score.
Weights are configurable via app config (TEXT_WEIGHT, FACE_WEIGHT).
Speech modality placeholder included for future expansion.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, Any, Dict

from app.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Face emotion → distress score mapping
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

# Expanded 16-state clinical affective distress mapping
VAST_EMOTION_DISTRESS_SCORES: dict[str, float] = {
    "panic_fear": 0.95,
    "anxious_hypervigilant": 0.85,
    "overwhelmed": 0.80,
    "grief_sorrow": 0.85,
    "shame_withdrawn": 0.75,
    "depressed_dejected": 0.75,
    "repressed_anger": 0.65,
    "agitated_restless": 0.70,
    "frustrated_tense": 0.55,
    "skeptical_guarded": 0.40,
    "cognitive_overload": 0.50,
    "fatigued_burnout": 0.60,
    "flat_affect": 0.50,
    "neutral_attentive": 0.15,
    "calm_serene": 0.05,
    "joyful_grounded": 0.05,
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
    triguna_dominant: str = "sattva"
    triguna_scores: Dict[str, float] = field(default_factory=lambda: {"sattva": 0.5, "rajas": 0.25, "tamas": 0.25})
    biometric_penalty: float = 0.0


class FusionEngine:
    """
    Computes the weighted multimodal risk score.

    Formula:
        final_risk_score = (TEXT_WEIGHT * text_distress) + (FACE_WEIGHT * face_distress)
        + biometric_somatic_penalty (from oculomotor & tension markers)

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
        """Map face emotion label → distress score (checks vast taxonomy first, then legacy)."""
        key = face_emotion.lower().replace(" ", "_")
        if key in VAST_EMOTION_DISTRESS_SCORES:
            return VAST_EMOTION_DISTRESS_SCORES[key]
        return FACE_DISTRESS_SCORES.get(key, 0.20)

    def compute(
        self,
        dominant_text_emotion: str,
        face_emotion: str,
        speech_score: Optional[float] = None,
        biometrics: Optional[Any] = None,
    ) -> FusionResult:
        """
        Compute weighted fusion score from available modalities.

        Args:
            dominant_text_emotion: Top emotion from DistilBERT (e.g. "sadness")
            face_emotion: Detected face emotion (e.g. "sad" or "anxious_hypervigilant")
            speech_score: Optional speech distress score (0.0–1.0)
            biometrics: Optional BiometricTelemetry instance or dict

        Returns:
            FusionResult with final weighted score, Triguna alignment, and breakdown
        """
        tw = self.settings.TEXT_WEIGHT
        fw = self.settings.FACE_WEIGHT

        text_score = self._text_distress(dominant_text_emotion)

        # Determine face score & biometric penalties
        biometric_penalty = 0.0
        effective_face_emotion = face_emotion
        triguna_dominant = "sattva"
        triguna_scores = {"sattva": 0.6, "rajas": 0.2, "tamas": 0.2}

        if biometrics:
            # Extract from Pydantic model or dict
            if hasattr(biometrics, "dominant_emotion"):
                effective_face_emotion = biometrics.dominant_emotion or face_emotion
                gaze = getattr(biometrics, "gaze_direction", "direct")
                bpm = getattr(biometrics, "blink_rate_bpm", 18.0)
                tension = getattr(biometrics, "facial_tension_index", 0.0)
                triguna = getattr(biometrics, "triguna_dominant", None)
                val = getattr(biometrics, "valence", 0.0)
                arousal = getattr(biometrics, "arousal", 0.0)
            elif isinstance(biometrics, dict):
                effective_face_emotion = biometrics.get("dominant_emotion", face_emotion)
                gaze = biometrics.get("gaze_direction", "direct")
                bpm = biometrics.get("blink_rate_bpm", 18.0)
                tension = biometrics.get("facial_tension_index", 0.0)
                triguna = biometrics.get("triguna_dominant", None)
                val = biometrics.get("valence", 0.0)
                arousal = biometrics.get("arousal", 0.0)
            else:
                gaze, bpm, tension, triguna, val, arousal = "direct", 18.0, 0.0, None, 0.0, 0.0

            # Oculomotor distress penalty
            if gaze == "downcast":
                biometric_penalty += 0.08  # Shame/withdrawal
            elif gaze == "darting":
                biometric_penalty += 0.10  # Hypervigilance/anxiety saccades
            
            # Blink stress penalty
            if bpm > 28:
                biometric_penalty += 0.06  # Sympathetic nervous hyperarousal
            elif bpm < 10:
                biometric_penalty += 0.04  # Emotional blunting / fatigue

            # Facial tension penalty
            if tension > 0.40:
                biometric_penalty += round(tension * 0.10, 3)

            # Compute Triguna distribution
            r_score = min(1.0, arousal * 0.5 + (0.3 if gaze == "darting" else 0.0) + (0.2 if bpm > 26 else 0.0))
            t_score = min(1.0, max(0.0, -val) * 0.5 + (0.3 if gaze == "downcast" else 0.0) + (0.2 if bpm < 12 else 0.0))
            s_score = max(0.0, 1.0 - (r_score + t_score) / 2)
            tot = (r_score + t_score + s_score) or 1.0

            triguna_scores = {
                "sattva": round(s_score / tot, 3),
                "rajas": round(r_score / tot, 3),
                "tamas": round(t_score / tot, 3),
            }
            if triguna:
                triguna_dominant = triguna
            else:
                triguna_dominant = max(triguna_scores, key=triguna_scores.get)

        face_score = self._face_distress(effective_face_emotion)

        # Base fusion
        total = tw + fw
        base_final = ((tw / total) * text_score) + ((fw / total) * face_score)
        final = min(1.0, base_final + (biometric_penalty * 0.35))
        final = round(min(max(final, 0.0), 1.0), 4)

        # Determine dominant modality
        if abs(text_score - face_score) < 0.10:
            dominant = "balanced"
        elif text_score > face_score:
            dominant = "text"
        else:
            dominant = "face"

        logger.debug(
            "Fusion: text=%s(%.2f) face=%s(%.2f) penalty=%.2f triguna=%s → final=%.4f dominant=%s",
            dominant_text_emotion, text_score,
            effective_face_emotion, face_score,
            biometric_penalty, triguna_dominant,
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
            triguna_dominant=triguna_dominant,
            triguna_scores=triguna_scores,
            biometric_penalty=round(biometric_penalty, 3),
        )


# Singleton
fusion_engine = FusionEngine()
