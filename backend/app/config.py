"""
config.py — PsyPredict Production Configuration
All settings loaded from environment variables via Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # ── LLM Provider Selection ────────────────────────────────────────────────
    # "groq" (default, for HF Spaces) or "ollama" (local development)
    LLM_PROVIDER: str = "groq"

    # ── Groq API (cloud LLM inference) ────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # ── Ollama (local LLM inference) ──────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL_NAME: str = "llama3"
    OLLAMA_TIMEOUT_S: int = 120
    OLLAMA_RETRIES: int = 3
    OLLAMA_RETRY_DELAY_S: float = 2.0

    # ── Legacy compat (health endpoint previously read these) ─────────────────
    OLLAMA_MODEL: str = "llama3"

    # ── DistilBERT Text Emotion ───────────────────────────────────────────────
    DISTILBERT_MODEL: str = "bhadresh-savani/distilbert-base-uncased-emotion"

    # ── Crisis Detection ──────────────────────────────────────────────────────
    CRISIS_THRESHOLD: float = 0.65

    # ── Multimodal Fusion Weights (must sum to ~1.0) ──────────────────────────
    TEXT_WEIGHT: float = 0.65
    FACE_WEIGHT: float = 0.35

    # ── Context Window ────────────────────────────────────────────────────────
    MAX_CONTEXT_TURNS: int = 10

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT: str = "30/minute"

    # ── Input Sanitization ───────────────────────────────────────────────────
    MAX_INPUT_CHARS: int = 2000

    # Patient Memory — Adaptive Learning
    PATIENT_MEMORY_BACKEND: str = "sqlite"  # "sqlite" (local, default) or "supabase"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    PATIENT_HISTORY_MAX_SESSIONS: int = 20
    SQLITE_DB_PATH: str = ""  # Auto-detected if empty

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Returns a cached singleton Settings instance."""
    return Settings()
