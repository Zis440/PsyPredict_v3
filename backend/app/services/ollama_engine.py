"""
ollama_engine.py — Backwards-Compatible LLM Shim

This module previously contained the full Groq/Ollama implementation.
It now delegates to the provider abstraction layer (llm_provider.py).

The singleton `ollama_engine` is preserved so all existing imports
throughout the codebase continue to work without changes:

    from app.services.ollama_engine import ollama_engine
"""
from app.services.llm_provider import get_llm_client

# Singleton — same name so all existing imports work unchanged.
# Points to the active provider (GroqClient or OllamaClient) based on
# the LLM_PROVIDER environment variable.
ollama_engine = get_llm_client()
