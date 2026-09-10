# ─────────────────────────────────────────────────────────────────────────────
# PsyPredict — Backend Dockerfile for Hugging Face Spaces (CPU Basic)
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.10-slim

# ── 1. System dependencies ────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ── 2. Setup user with UID 1000 (Required by Hugging Face Spaces Docker) ──────
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /home/user/app

# ── 3. PyTorch CPU-only (separate layer — caches very well) ───────────────────
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

# ── 4. Install remaining Python dependencies ──────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── 5. Copy application source code with user ownership ───────────────────────
COPY --chown=user:user . .

# Ensure data directories exist and have proper permissions for user 1000
RUN mkdir -p /home/user/app/app/data/index_cache \
    && mkdir -p /home/user/.cache \
    && chown -R user:user /home/user

USER user

# ── 6. Download ML assets (Face emotion model) ────────────────────────────────
ENV HF_HUB_OFFLINE=0
RUN python download_models.py || true

# ── 7. Runtime environment ────────────────────────────────────────────────────
ENV PYTHONPATH=/home/user/app
ENV OLLAMA_TIMEOUT_S=30
ENV OLLAMA_RETRIES=3
ENV HF_HUB_OFFLINE=0
ENV LOG_LEVEL=INFO
ENV RATE_LIMIT=30/minute

# ── 8. Expose HF Spaces standard port ────────────────────────────────────────
EXPOSE 7860

# ── 9. Launch FastAPI directly via Uvicorn ────────────────────────────────────
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860} --workers 1 --log-level info"]
