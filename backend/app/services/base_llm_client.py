"""
base_llm_client.py — Abstract LLM Client Interface for PsyPredict

All LLM providers (Groq, Ollama, future providers) must implement
this interface to ensure consistent behaviour across the application.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Optional

from app.schemas import ConversationMessage, PsychReport


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM inference clients.

    Concrete implementations:
      - GroqClient  — Groq cloud API (OpenAI-compatible)
      - OllamaClient — Local Ollama server (HTTP)
    """

    @abstractmethod
    async def generate(
        self,
        user_text: str,
        face_emotion: str = "neutral",
        history: Optional[List[ConversationMessage]] = None,
        text_emotion_summary: Optional[str] = None,
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> tuple[str, PsychReport]:
        """
        Generate a complete (non-streaming) response.

        Returns:
            (reply_text, PsychReport) — the conversational reply and
            the structured psychological assessment.
        """
        ...

    @abstractmethod
    async def generate_stream(
        self,
        user_text: str,
        face_emotion: str = "neutral",
        history: Optional[List[ConversationMessage]] = None,
        text_emotion_summary: Optional[str] = None,
        patient_profile: Optional[str] = None,
        gita_context: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Yield raw text tokens as they arrive from the LLM.

        The caller is responsible for buffering the full response
        and parsing it into a PsychReport after streaming completes.
        """
        ...

    @abstractmethod
    async def is_reachable(self) -> bool:
        """
        Returns True if the underlying LLM service is reachable
        and ready to accept requests.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """
        Clean up any persistent connections or resources.
        Called during application shutdown.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier (e.g. 'groq', 'ollama')."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The model name/tag being used (e.g. 'llama-3.3-70b-versatile')."""
        ...

    @property
    @abstractmethod
    def base_url(self) -> str:
        """The base URL of the provider's API endpoint."""
        ...
