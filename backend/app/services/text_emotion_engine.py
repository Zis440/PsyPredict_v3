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
            device=-1,            # Force CPU (prevents ZeroGPU CUDA init crash)
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

    def _fallback_classify(self, text: str) -> List[EmotionLabel]:
        """
        Fast, zero-dependency psychological sentiment & emotion classifier.
        Used on lightweight cloud deployments or when DistilBERT is not loaded.
        """
        LEXICON = {
            "sadness": ["sad", "depressed", "unhappy", "hopeless", "crying", "grief", "miserable", "down", "lonely", "hurt", "despair", "empty", "loss", "tired", "giving up", "pain"],
            "joy": ["happy", "great", "joy", "excited", "cheerful", "delighted", "love", "wonderful", "glad", "better", "grateful", "blessed", "smiling", "peaceful", "good"],
            "fear": ["anxious", "anxiety", "afraid", "scared", "fear", "panic", "worried", "nervous", "terrified", "dread", "stress", "stressed", "overwhelmed", "frightened"],
            "anger": ["angry", "mad", "furious", "hate", "irritated", "annoyed", "rage", "frustrated", "resentful", "hostile", "disgusted", "bitter"],
            "surprise": ["shocked", "surprised", "unexpected", "astonished", "sudden", "stunned", "disbelief"],
        }
        t = text.lower()
        scores = {}
        matched = False
        for emotion, words in LEXICON.items():
            count = sum(1 for w in words if w in t)
            if count > 0:
                matched = True
            scores[emotion] = 0.05 + count * 0.40

        scores["neutral"] = 0.60 if not matched else 0.05

        total = sum(scores.values())
        labels = [
            EmotionLabel(label=emo, score=round(score / total, 4))
            for emo, score in scores.items()
        ]
        return sorted(labels, key=lambda x: x.score, reverse=True)

    def _classify_sync(self, text: str) -> List[EmotionLabel]:
        if _pipeline is not None:
            try:
                results = _pipeline(text[:512])
                if results:
                    raw = results[0] if isinstance(results[0], list) else results
                    labels = [
                        EmotionLabel(label=item["label"].lower(), score=round(item["score"], 4))
                        for item in raw
                    ]
                    return sorted(labels, key=lambda x: x.score, reverse=True)
            except Exception as exc:
                logger.error("DistilBERT inference error: %s", exc)
        return self._fallback_classify(text)

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
