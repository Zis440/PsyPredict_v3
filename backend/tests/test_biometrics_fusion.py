import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas import BiometricTelemetry, ChatRequest
from app.services.fusion_engine import fusion_engine
from app.services.llm_shared import build_messages, format_multimodal_context
from app.services.emotion_engine import emotion_detector, VAST_EMOTION_TAXONOMY


def test_biometric_telemetry_schema():
    """Verify BiometricTelemetry Pydantic model parses and validates fields."""
    data = {
        "dominant_emotion": "anxious_hypervigilant",
        "confidence": 88.5,
        "valence": -0.65,
        "arousal": 0.82,
        "distress_score": 0.78,
        "gaze_direction": "darting",
        "eye_contact_ratio": 0.45,
        "blink_rate_bpm": 34.0,
        "facial_tension_index": 0.62,
        "triguna_dominant": "rajas",
        "notes": "Hyperarousal and restless saccades",
    }
    telemetry = BiometricTelemetry(**data)
    assert telemetry.dominant_emotion == "anxious_hypervigilant"
    assert telemetry.gaze_direction == "darting"
    assert telemetry.triguna_dominant == "rajas"
    assert telemetry.blink_rate_bpm == 34.0

    # Verify ChatRequest accepts biometrics
    chat_req = ChatRequest(
        message="I have a terrible headache and cannot focus",
        emotion="anxious_hypervigilant",
        biometrics=telemetry,
    )
    assert chat_req.biometrics is not None
    assert chat_req.biometrics.triguna_dominant == "rajas"


def test_fusion_engine_with_biometrics():
    """Verify FusionEngine calculates Triguna and oculomotor stress penalties."""
    telemetry = BiometricTelemetry(
        dominant_emotion="anxious_hypervigilant",
        confidence=90.0,
        valence=-0.70,
        arousal=0.85,
        distress_score=0.85,
        gaze_direction="darting",
        eye_contact_ratio=0.30,
        blink_rate_bpm=36.0,
        facial_tension_index=0.65,
        triguna_dominant="rajas",
    )

    result = fusion_engine.compute(
        dominant_text_emotion="fear",
        face_emotion="anxious_hypervigilant",
        biometrics=telemetry,
    )

    assert result.triguna_dominant == "rajas"
    assert result.biometric_penalty > 0
    assert 0.0 <= result.final_risk_score <= 1.0


def test_fusion_engine_tamas_downcast():
    """Verify downcast gaze and dejection maps to Tamas."""
    telemetry = BiometricTelemetry(
        dominant_emotion="depressed_dejected",
        confidence=87.0,
        valence=-0.80,
        arousal=0.20,
        distress_score=0.75,
        gaze_direction="downcast",
        eye_contact_ratio=0.25,
        blink_rate_bpm=9.0,
        facial_tension_index=0.20,
        triguna_dominant="tamas",
    )

    result = fusion_engine.compute(
        dominant_text_emotion="sadness",
        face_emotion="depressed_dejected",
        biometrics=telemetry,
    )

    assert result.triguna_dominant == "tamas"
    assert result.final_risk_score >= 0.70


def test_format_multimodal_context():
    """Verify prompt formatting outputs the clinical observation block."""
    telemetry = BiometricTelemetry(
        dominant_emotion="anxious_hypervigilant",
        confidence=90.0,
        valence=-0.65,
        arousal=0.80,
        distress_score=0.75,
        gaze_direction="darting",
        eye_contact_ratio=0.40,
        blink_rate_bpm=32.0,
        facial_tension_index=0.55,
        triguna_dominant="rajas",
    )

    ctx = format_multimodal_context(
        face_emotion="anxious_hypervigilant",
        text_emotion_summary="fear (0.89)",
        biometrics=telemetry,
    )

    assert "[LIVE BIOMETRIC & OCULOMOTOR OBSERVATIONS]" in ctx
    assert "DARTING" in ctx
    assert "RAJAS" in ctx
    assert "THERAPIST INSTRUCTION" in ctx


def test_vast_emotion_taxonomy():
    """Verify vast emotion taxonomy has at least 16 classes."""
    assert len(VAST_EMOTION_TAXONOMY) >= 16
    assert "anxious_hypervigilant" in VAST_EMOTION_TAXONOMY
    assert "joyful_grounded" in VAST_EMOTION_TAXONOMY
    assert "flat_affect" in VAST_EMOTION_TAXONOMY


if __name__ == "__main__":
    test_biometric_telemetry_schema()
    test_fusion_engine_with_biometrics()
    test_fusion_engine_tamas_downcast()
    test_format_multimodal_context()
    test_vast_emotion_taxonomy()
    print("All biometrics & fusion tests passed successfully!")
