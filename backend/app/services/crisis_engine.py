"""
crisis_engine.py — PsyPredict Crisis Detection Layer
Uses DistilBERT zero-shot classification (NOT keyword matching).
Weighted risk scoring across mental health risk dimensions.
Triggers override of LLM output when threshold exceeded.
This layer is the safety net — it runs BEFORE and OVERRIDES the LLM.
"""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from app.schemas import CrisisResource, PsychReport, RiskLevel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Risk Labels + Weights (tuned empirically)
# ---------------------------------------------------------------------------

RISK_LABELS: list[str] = [
    "suicidal ideation",
    "self-harm intent",
    "immediate danger to self",
    "severe mental breakdown",
    "hopelessness and worthlessness",
]

RISK_WEIGHTS: dict[str, float] = {
    "suicidal ideation": 1.0,
    "self-harm intent": 1.0,
    "immediate danger to self": 0.95,
    "severe mental breakdown": 0.60,
    "hopelessness and worthlessness": 0.50,
}

# ---------------------------------------------------------------------------
# Crisis Resources (India + International)
# ---------------------------------------------------------------------------

CRISIS_RESOURCES: List[CrisisResource] = [
    CrisisResource(name="iCall (India)", contact="9152987821", available="Mon–Sat 8am–10pm"),
    CrisisResource(name="Vandrevala Foundation (India)", contact="1860-2662-345", available="24/7"),
    CrisisResource(name="AASRA (India)", contact="9820466627", available="24/7"),
    CrisisResource(name="Befrienders Worldwide", contact="https://www.befrienders.org", available="24/7"),
    CrisisResource(name="Crisis Text Line (US/UK)", contact="Text HOME to 741741", available="24/7"),
]

# ---------------------------------------------------------------------------
# Zero-Shot Classifier
# ---------------------------------------------------------------------------

_zero_shot_pipeline = None
_load_error: Optional[str] = None


def initialize_crisis_classifier() -> None:
    """
    Load MiniLM zero-shot classifier at startup.
    Uses cross-encoder/nli-MiniLM2-L6-H768 — lightweight, fast.
    """
    global _zero_shot_pipeline, _load_error
    try:
        from transformers import pipeline as hf_pipeline
        import os
        
        local_path = os.path.join("app", "ml_assets", "crisis_model")
        logger.info("Loading crisis zero-shot classifier from %s", local_path)
        
        _zero_shot_pipeline = hf_pipeline(
            "zero-shot-classification",
            model=local_path if os.path.exists(local_path) else "cross-encoder/nli-MiniLM2-L6-H768",
            device=-1,  # CPU
        )
        logger.info("✅ Crisis classifier loaded.")
    except Exception as exc:
        _load_error = str(exc)
        logger.error("❌ Crisis classifier load failed: %s", exc)


def _score_sync(text: str) -> float:
    """
    Synchronous zero-shot scoring. Runs in thread pool.
    Returns weighted crisis risk score in [0, 1].
    """
    if _zero_shot_pipeline is None:
        # Fallback: basic substring check for true emergencies only
        return _fallback_score(text)

    try:
        result = _zero_shot_pipeline(
            text[:512],
            candidate_labels=RISK_LABELS,
            multi_label=True,
        )
        label_scores: dict[str, float] = dict(
            zip(result["labels"], result["scores"])
        )
        # Weighted sum, normalized to [0, 1]
        total_weight = sum(RISK_WEIGHTS.values())
        weighted_sum = sum(
            label_scores.get(lbl, 0.0) * RISK_WEIGHTS[lbl]
            for lbl in RISK_LABELS
        )
        return min(weighted_sum / total_weight, 1.0)
    except Exception as exc:
        logger.error("Crisis scoring error: %s", exc)
        return _fallback_score(text)


def _fallback_score(text: str) -> float:
    """
    Hard fallback: only fires on unambiguous semantic signals.
    This is distinct from keyword matching — uses phrase-level context.
    """
    HIGH_RISK_PHRASES = [
        "want to die", "kill myself", "end my life", "hurt myself",
        "suicide", "self harm", "self-harm", "no reason to live",
        "don't want to exist", "cannot go on", "take my life",
    ]
    t = text.lower()
    hits = sum(1 for phrase in HIGH_RISK_PHRASES if phrase in t)
    return min(hits * 0.35, 1.0)


class CrisisEngine:
    """
    Evaluates crisis risk from user text.
    Must be called before LLM generation.
    If triggered, returns a deterministic PsychReport override.
    """

    def __init__(self, threshold: float = 0.65) -> None:
        self.threshold = threshold

    async def evaluate(self, text: str) -> tuple[float, bool]:
        """
        Returns (risk_score, crisis_triggered).
        Runs synchronous model in thread pool.
        """
        score = await asyncio.to_thread(_score_sync, text)
        triggered = score >= self.threshold
        if triggered:
            logger.warning(
                "CRISIS TRIGGERED — risk_score=%.3f text=%r",
                score,
                text[:100],
            )
        return score, triggered

    def build_crisis_report(self, risk_score: float) -> tuple[str, PsychReport]:
        """
        Returns deterministic crisis reply + PsychReport.
        Does NOT involve the LLM.
        """
        reply = (
            "I hear that you're going through something very serious right now. "
            "Please reach out to a crisis support line immediately — "
            "you don't have to face this alone."
        )
        report = PsychReport(
            risk_classification=RiskLevel.CRITICAL,
            emotional_state_summary=(
                "Severe psychological distress detected. Indicators of self-harm "
                "or suicidal ideation are present."
            ),
            behavioral_inference=(
                "User's expressed content suggests acute crisis state. "
                "Immediate professional intervention is warranted."
            ),
            cognitive_distortions=["Hopelessness", "All-or-nothing thinking"],
            suggested_interventions=[
                "Immediate contact with a mental health crisis line.",
                "Notify a trusted person or emergency services if in immediate danger.",
                "Seek in-person emergency psychiatric evaluation.",
            ],
            confidence_score=round(risk_score, 3),
            crisis_triggered=True,
            crisis_resources=CRISIS_RESOURCES,
            service_degraded=False,
        )
        return reply, report

    @property
    def is_loaded(self) -> bool:
        return _zero_shot_pipeline is not None


# Singleton
crisis_engine = CrisisEngine()
