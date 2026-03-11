#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# start.sh — PsyPredict HF Spaces Startup Orchestrator
#
# Execution order:
#   1. Start Ollama server daemon in the background
#   2. Wait until Ollama API is healthy (up to 60 seconds)
#   3. Pull the Phi-3.5 quantized model (skips if already cached in this run)
#   4. Launch FastAPI / Uvicorn on port 7860
#
# Environment variables (set in Dockerfile or HF Space secrets):
#   OLLAMA_MODEL  — model tag to pull (default: phi3.5:3.8b-mini-instruct-q4_0)
# ─────────────────────────────────────────────────────────────────────────────

set -e  # Exit immediately on any error

echo "═══════════════════════════════════════════════"
echo "🚀  PsyPredict — Hugging Face Spaces Startup"
echo "═══════════════════════════════════════════════"

# ── Step 1: Start Ollama server in the background ─────────────────────────────
echo "▶  Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# ── Step 2: Wait for Ollama to become healthy (max 60 seconds) ────────────────
echo "⏳  Waiting for Ollama to be ready..."
RETRIES=30
for i in $(seq 1 $RETRIES); do
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅  Ollama is ready (attempt $i/$RETRIES)."
        break
    fi
    if [ "$i" -eq "$RETRIES" ]; then
        echo "❌  Ollama failed to start within 60 seconds. Exiting."
        exit 1
    fi
    sleep 2
done

# ── Step 3: Pull the Phi-3.5 model ────────────────────────────────────────────
# 'ollama pull' is idempotent — safe to call even if the model is cached.
# On HF Spaces, the first pull will download ~2.4 GB; subsequent restarts
# are faster because the container's /root/.ollama layer is reused.
MODEL="${OLLAMA_MODEL:-phi3.5:3.8b-mini-instruct-q4_0}"
echo "▶  Pulling model: $MODEL"
echo "   (First run downloads ~2.4 GB — may take several minutes on CPU)"
ollama pull "$MODEL"
echo "✅  Model ready: $MODEL"

# ── Step 4: Launch FastAPI on port 7860 ───────────────────────────────────────
echo "▶  Starting FastAPI (Uvicorn) on port 7860..."
echo "   API docs → http://localhost:7860/docs"
echo "═══════════════════════════════════════════════"
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 7860 \
    --workers 1 \
    --log-level info
