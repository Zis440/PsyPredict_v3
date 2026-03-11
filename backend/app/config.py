"""
config.py — PsyPredict Production Configuration
All settings loaded from environment variables via Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Ollama / LLM (Centralized API)
    # Update this to your DigitalOcean/VPS IP address where Ollama is running
    # Default is localhost (e.g. for development), but in production it should be like:
    # OLLAMA_BASE_URL: str = "http://123.45.67.89:11434"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "phi3.5:3.8b-mini-instruct-q4_0"
    OLLAMA_TIMEOUT_S: int = 90
    
    # Retry logic for external LLM API
    OLLAMA_RETRIES: int = 3
    OLLAMA_RETRY_DELAY_S: float = 2.0

    # DistilBERT Text Emotion
    DISTILBERT_MODEL: str = "bhadresh-savani/distilbert-base-uncased-emotion"

    # Crisis Detection
    CRISIS_THRESHOLD: float = 0.65

    # Multimodal Fusion Weights (must sum to ~1.0)
    TEXT_WEIGHT: float = 0.65
    FACE_WEIGHT: float = 0.35

    # Context Window
    MAX_CONTEXT_TURNS: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    RATE_LIMIT: str = "30/minute"

    # Input Sanitization
    MAX_INPUT_CHARS: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",        # Ignore unknown env vars (e.g. old GOOGLE_API_KEY)
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Returns a cached singleton Settings instance."""
    return Settings()
