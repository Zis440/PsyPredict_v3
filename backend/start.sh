#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# start.sh — PsyPredict HF Spaces Startup Orchestrator
#
# Execution order:
#   1. Start Ollama server daemon in the background
#   2. Wait until Ollama API is healthy (up to 60 seconds)
#   3. Pull the configured model (skips if already cached in this run)
#   4. Launch FastAPI / Uvicorn on port 7860
#
# Environment variables (set in Dockerfile or HF Space secrets):
#   OLLAMA_MODEL_NAME — model tag to pull (default: llama3)
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

# ── Step 3: Pull the model ────────────────────────────────────────────────────
# Reads OLLAMA_MODEL_NAME — same variable used by config.py and .env.example.
# 'ollama pull' is idempotent — safe to call even if the model is cached.
MODEL="${OLLAMA_MODEL_NAME:-llama3}"
echo "▶  Pulling model: $MODEL"
echo "   (First run downloads ~4.7 GB — may take several minutes on CPU)"
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
