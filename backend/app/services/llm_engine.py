"""
llm_engine.py — DEPRECATED

This module was the original Gemini-based LLM engine.
The production pipeline now uses OllamaEngine (ollama_engine.py) exclusively.

This file is kept for backward compatibility — any imports will receive
a delegating wrapper that routes to OllamaEngine.
"""

import logging
import warnings

logger = logging.getLogger(__name__)

warnings.warn(
    "llm_engine.py is deprecated. Use ollama_engine.py (OllamaEngine) instead.",
    DeprecationWarning,
    stacklevel=2,
)


class LLMEngine:
    """
    DEPRECATED: Wrapper that delegates to OllamaEngine.
    Kept for backward compatibility only.
    """

    def __init__(self):
        self.model = None
        logger.warning(
            "LLMEngine (Gemini) is deprecated. "
            "All inference is handled by OllamaEngine. "
            "Remove references to llm_engine.py from your codebase."
        )

    def generate_response(self, user_text, emotion_context=None, history=[]):
        """
        DEPRECATED: Returns a message directing callers to use OllamaEngine.
        """
        return (
            "This engine is deprecated. PsyPredict now uses OllamaEngine for all inference. "
            "Please update your code to use the /api/chat endpoint."
        )


# Singleton — kept for any residual imports
llm_therapist = LLMEngine()