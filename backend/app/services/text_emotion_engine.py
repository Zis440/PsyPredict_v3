"""
text_emotion_engine.py — DistilBERT Multi-Label Text Emotion Classifier
Uses: bhadresh-savani/distilbert-base-uncased-emotion
Output: top-N emotions with calibrated confidence scores.
Runs inference in asyncio.to_thread to avoid blocking the event loop.
"""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from app.schemas import EmotionLabel

logger = logging.getLogger(__name__)

_pipeline = None
_load_error: Optional[str] = None


def _load_pipeline(model_name: str) -> None:
    """Called once at startup. Loads the HuggingFace pipeline into global."""
    global _pipeline, _load_error
    try:
        from transformers import pipeline as hf_pipeline
        import os
        
        # Determine local path
        local_path = os.path.join("app", "ml_assets", "distilbert_model")
        
        logger.info("Loading DistilBERT text emotion model from %s", local_path)
        _pipeline = hf_pipeline(
            "text-classification",
            model=local_path if os.path.exists(local_path) else model_name,
            top_k=None,           # Return ALL labels
            truncation=True,
            max_length=512,
        )
        logger.info("[OK] DistilBERT emotion model loaded successfully.")
    except Exception as exc:
        _load_error = str(exc)
        logger.error("[ERROR] Failed to load DistilBERT model: %s", exc)


def initialize(model_name: str) -> None:
    """Called at app startup to pre-warm the model."""
    _load_pipeline(model_name)


class TextEmotionEngine:
    """
    Wraps the HuggingFace DistilBERT pipeline for async use in FastAPI.
    """

    def _classify_sync(self, text: str) -> List[EmotionLabel]:
        if _pipeline is None:
            return []
        try:
            results = _pipeline(text[:512])
            if not results:
                return []
            # pipeline returns list-of-list when top_k=None
            raw = results[0] if isinstance(results[0], list) else results
            labels = [
                EmotionLabel(label=item["label"].lower(), score=round(item["score"], 4))
                for item in raw
            ]
            # Sort descending by score
            return sorted(labels, key=lambda x: x.score, reverse=True)
        except Exception as exc:
            logger.error("DistilBERT inference error: %s", exc)
            return []

    async def classify(self, text: str) -> List[EmotionLabel]:
        """
        Async wrapper — runs CPU-bound inference in a thread pool.
        Returns list of EmotionLabel sorted by confidence desc.
        """
        return await asyncio.to_thread(self._classify_sync, text)

    async def top_emotion(self, text: str) -> str:
        """Returns the single dominant emotion label."""
        labels = await self.classify(text)
        return labels[0].label if labels else "neutral"

    def summary_string(self, labels: List[EmotionLabel], top_k: int = 3) -> str:
        """
        Formats top-k labels as a string for LLM prompt injection.
        Example: "sadness(0.87), fear(0.08), anger(0.03)"
        """
        return ", ".join(
            f"{lbl.label}({lbl.score:.2f})" for lbl in labels[:top_k]
        )

    @property
    def is_loaded(self) -> bool:
        return _pipeline is not None

    @property
    def load_error(self) -> Optional[str]:
        return _load_error


# Singleton
text_emotion_engine = TextEmotionEngine()
