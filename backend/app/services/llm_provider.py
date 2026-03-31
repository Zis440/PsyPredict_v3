"""
llm_provider.py — LLM Provider Factory for PsyPredict

Reads LLM_PROVIDER from settings and returns the appropriate
singleton client. Handles graceful fallback if Ollama is configured
but Groq key is available as backup.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from app.config import get_settings
from app.services.base_llm_client import BaseLLMClient

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm_client() -> BaseLLMClient:
    """
    Factory that returns the active LLM client singleton based on
    the LLM_PROVIDER environment variable.

    Supported values:
      - "groq"   → GroqClient (default, for HF Spaces)
      - "ollama" → OllamaClient (local development)

    Invalid values fall back to Groq with a warning.
    """
    settings = get_settings()
    provider = settings.LLM_PROVIDER.strip().lower()

    if provider == "ollama":
        from app.services.ollama_client import OllamaClient

        logger.info(
            "LLM Provider: ollama (base_url=%s, model=%s)",
            settings.OLLAMA_BASE_URL,
            settings.OLLAMA_MODEL_NAME,
        )
        return OllamaClient()

    if provider == "groq":
        from app.services.groq_client import GroqClient

        logger.info(
            "LLM Provider: groq (model=%s, key=%s)",
            settings.GROQ_MODEL,
            "set" if settings.GROQ_API_KEY else "NOT SET",
        )
        return GroqClient()

    # Unknown provider — warn and fall back to Groq
    logger.warning(
        "Unknown LLM_PROVIDER=%r — falling back to 'groq'. "
        "Valid values: 'groq', 'ollama'.",
        provider,
    )
    from app.services.groq_client import GroqClient

    return GroqClient()
