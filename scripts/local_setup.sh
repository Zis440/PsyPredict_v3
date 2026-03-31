#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# PsyPredict — Local Development Setup (Ollama + Backend)
#
# Usage:
#   chmod +x scripts/local_setup.sh
#   ./scripts/local_setup.sh
#
# This script:
#   1. Checks if Ollama is installed
#   2. Starts Ollama server if not running
#   3. Pulls the llama3 model
#   4. Sets up the .env for local Ollama mode
#   5. Starts the PsyPredict backend
# ─────────────────────────────────────────────────────────────────────────────

set -e

echo "═══════════════════════════════════════════════"
echo "🧠  PsyPredict — Local Development Setup"
echo "═══════════════════════════════════════════════"

# ── Step 1: Check Ollama installation ─────────────────────────────────────────
if ! command -v ollama &> /dev/null; then
    echo "❌  Ollama is not installed."
    echo "   Install it from: https://ollama.com/download"
    echo "   macOS:  brew install ollama"
    echo "   Linux:  curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi
echo "✅  Ollama found: $(ollama --version 2>/dev/null || echo 'installed')"

# ── Step 2: Start Ollama server if not running ────────────────────────────────
if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅  Ollama server already running."
else
    echo "▶  Starting Ollama server in background..."
    ollama serve &
    OLLAMA_PID=$!

    # Wait for startup
    echo "⏳  Waiting for Ollama to be ready..."
    for i in $(seq 1 15); do
        if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅  Ollama is ready (attempt $i/15)."
            break
        fi
        if [ "$i" -eq "15" ]; then
            echo "❌  Ollama failed to start within 30 seconds."
            exit 1
        fi
        sleep 2
    done
fi

# ── Step 3: Pull the Llama3 model ────────────────────────────────────────────
MODEL="${OLLAMA_MODEL_NAME:-llama3}"
echo "▶  Pulling model: $MODEL"
echo "   (First run downloads ~4.7 GB — may take several minutes)"
ollama pull "$MODEL"
echo "✅  Model ready: $MODEL"

# ── Step 4: Configure environment ─────────────────────────────────────────────
cd "$(dirname "$0")/../backend"

if [ ! -f .env ]; then
    echo "▶  Creating .env from .env.example..."
    cp .env.example .env
fi

# Ensure Ollama mode is set
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL_NAME="$MODEL"

echo ""
echo "═══════════════════════════════════════════════"
echo "▶  Starting PsyPredict Backend (Ollama mode)"
echo "   LLM_PROVIDER=$LLM_PROVIDER"
echo "   OLLAMA_BASE_URL=$OLLAMA_BASE_URL"
echo "   OLLAMA_MODEL_NAME=$OLLAMA_MODEL_NAME"
echo "═══════════════════════════════════════════════"

# ── Step 5: Start the backend ─────────────────────────────────────────────────
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 7860 \
    --reload \
    --log-level info
