# ─────────────────────────────────────────────────────────────────────────────
# PsyPredict — Backend Dockerfile for Hugging Face Spaces (CPU / Docker SDK)
#
# Architecture:
#   - Ollama binary installed inside the container (serves Phi-3.5 on port 11434)
#   - FastAPI app served by Uvicorn on port 7860 (HF Spaces standard port)
#   - start.sh orchestrates: Ollama → model pull → Uvicorn
#   - ML assets (Keras face model + CSV) are downloaded at BUILD time via gdown
#   - DistilBERT + Crisis classifier are downloaded at BUILD time from HF Hub
#   - HF_HUB_OFFLINE=1 at runtime so the container starts offline-capable
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.10-slim

WORKDIR /app

# ── 1. System dependencies ────────────────────────────────────────────────────
# libgl1 + libglib2.0-0: OpenCV headless needs these
# curl + ca-certificates: needed to download Ollama install script
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    ca-certificates \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# ── 2. Install Ollama binary ──────────────────────────────────────────────────
# Uses the official install script — places `ollama` binary in /usr/local/bin
RUN curl -fsSL https://ollama.com/install.sh | sh

# ── 3. PyTorch CPU-only (separate layer — ~800MB, caches very well) ───────────
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

# ── 4. Install remaining Python dependencies ──────────────────────────────────
# Note: torch is already installed above; pip will skip it when it hits
# the torch line in requirements.txt (version constraint already satisfied).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── 5. Copy application source code ──────────────────────────────────────────
COPY . .

# ── 6. Download ML assets at BUILD time ──────────────────────────────────────
# Downloads:
#   - app/ml_assets/emotion_model_trained.h5  (Keras CNN face model, ~4MB, Google Drive)
#   - app/ml_assets/MEDICATION.csv            (remedy database, Google Drive)
#   - app/ml_assets/distilbert_model/         (DistilBERT emotion classifier, ~260MB, HF Hub)
#   - app/ml_assets/crisis_model/             (MiniLM zero-shot classifier, ~130MB, HF Hub)
#
# Skips files that already exist in the build context (e.g. haarcascade XML).
# HF_HUB_OFFLINE must be 0 here so transformers can reach HuggingFace.
ENV HF_HUB_OFFLINE=0
RUN python download_models.py

# ── 7. Runtime environment ────────────────────────────────────────────────────
ENV PYTHONPATH=/app
# Ollama runs locally inside the container
ENV OLLAMA_BASE_URL=http://localhost:11434
ENV OLLAMA_MODEL=phi3.5:3.8b-mini-instruct-q4_0
ENV OLLAMA_TIMEOUT_S=300
ENV OLLAMA_RETRIES=2
# All HF models were baked in at build time — go offline for faster startup
ENV HF_HUB_OFFLINE=1
ENV LOG_LEVEL=INFO
ENV RATE_LIMIT=30/minute

# ── 8. Expose HF Spaces standard port ────────────────────────────────────────
EXPOSE 7860

# ── 9. Startup script ─────────────────────────────────────────────────────────
# start.sh: starts Ollama daemon → pulls Phi-3.5 model → launches Uvicorn
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
