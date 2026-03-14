# ─────────────────────────────────────────────────────────────────────────────
# PsyPredict — Backend Dockerfile for Hugging Face Spaces
#
# Architecture:
#   - LLM inference via Groq API (no Ollama needed)
#   - FastAPI app served by Uvicorn on port 7860 (HF Spaces standard port)
#   - ML assets (Keras face model + CSV) downloaded at BUILD time via gdown
#   - DistilBERT + Crisis classifier downloaded at BUILD time from HF Hub
#   - HF_HUB_OFFLINE=1 at runtime so the container starts offline-capable
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.10-slim

WORKDIR /app

# ── 1. System dependencies ────────────────────────────────────────────────────
# libgl1 + libglib2.0-0: OpenCV headless needs these
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ── 2. PyTorch CPU-only (separate layer — ~800MB, caches very well) ───────────
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

# ── 3. Install remaining Python dependencies ──────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── 4. Copy application source code ──────────────────────────────────────────
COPY . .

# ── 5. Download ML assets at BUILD time ──────────────────────────────────────
# Downloads:
#   - app/ml_assets/emotion_model_trained.h5  (Keras CNN face model, ~4MB, Google Drive)
#   - app/ml_assets/MEDICATION.csv            (remedy database, Google Drive)
#   - app/ml_assets/distilbert_model/         (DistilBERT emotion classifier, ~260MB, HF Hub)
#   - app/ml_assets/crisis_model/             (MiniLM zero-shot classifier, ~130MB, HF Hub)
ENV HF_HUB_OFFLINE=0
RUN python download_models.py

# ── 6. Runtime environment ────────────────────────────────────────────────────
ENV PYTHONPATH=/app
ENV OLLAMA_TIMEOUT_S=30
ENV OLLAMA_RETRIES=3
ENV HF_HUB_OFFLINE=1
ENV LOG_LEVEL=INFO
ENV RATE_LIMIT=30/minute

# ── 7. Expose HF Spaces standard port ────────────────────────────────────────
EXPOSE 7860

# ── 8. Launch FastAPI directly (no Ollama needed) ────────────────────────────
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1", "--log-level", "info"]
