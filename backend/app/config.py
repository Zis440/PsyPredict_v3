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
    # OLLAMA_MODEL_NAME is the canonical variable used everywhere:
    #   config.py, .env, .env.example, start.sh, docker-compose.yml
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL_NAME: str = "llama3"
    OLLAMA_TIMEOUT_S: int = 120
    OLLAMA_RETRIES: int = 3
    OLLAMA_RETRY_DELAY_S: float = 2.0

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

    # ── LLM Orchestrator ──────────────────────────────────────────────────────
    LLM_ORCHESTRATOR_ENABLED: bool = True     # Use dual-LLM orchestrator
    CLOUD_FALLBACK_ENABLED: bool = True       # Fall back to Groq if Ollama fails
    LOCAL_FALLBACK_ENABLED: bool = True        # Fall back to Ollama if Groq fails
    PII_SCRUB_BEFORE_CLOUD: bool = True        # Redact PII before cloud calls

    # ── Knowledge Index (FAISS) ───────────────────────────────────────────────
    KNOWLEDGE_INDEX_ENABLED: bool = True
    KNOWLEDGE_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    KNOWLEDGE_INDEX_TOP_K: int = 3
    KNOWLEDGE_INDEX_CACHE_DIR: str = ""        # Auto-detected if empty

    # ── Patient Memory — Adaptive Learning ───────────────────────────────────
    PATIENT_MEMORY_BACKEND: str = "sqlite"  # "sqlite" (local, default) or "supabase"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    PATIENT_HISTORY_MAX_SESSIONS: int = 20
    SQLITE_DB_PATH: str = ""  # Auto-detected if empty

    # ── Session Summarization ─────────────────────────────────────────────────
    SESSION_SUMMARY_ENABLED: bool = True       # Auto-summarize sessions
    PROGRESS_TRACKING_ENABLED: bool = True     # Track patient progress over time

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Returns a cached singleton Settings instance."""
    return Settings()
