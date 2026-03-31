# ─────────────────────────────────────────────────────────────────────────────
# PsyPredict — Local Development Setup (Ollama + Backend) — Windows PowerShell
#
# Usage:
#   .\scripts\local_setup.ps1
#
# This script:
#   1. Checks if Ollama is installed
#   2. Starts Ollama server if not running
#   3. Pulls the llama3 model
#   4. Sets up the .env for local Ollama mode
#   5. Starts the PsyPredict backend
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🧠  PsyPredict — Local Development Setup" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan

# ── Step 1: Check Ollama installation ─────────────────────────────────────────
$ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaPath) {
    Write-Host "❌  Ollama is not installed." -ForegroundColor Red
    Write-Host "   Download from: https://ollama.com/download" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅  Ollama found: $($ollamaPath.Source)" -ForegroundColor Green

# ── Step 2: Start Ollama server if not running ────────────────────────────────
$ollamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        $ollamaRunning = $true
        Write-Host "✅  Ollama server already running." -ForegroundColor Green
    }
} catch {
    $ollamaRunning = $false
}

if (-not $ollamaRunning) {
    Write-Host "▶  Starting Ollama server in background..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

    Write-Host "⏳  Waiting for Ollama to be ready..." -ForegroundColor Yellow
    $ready = $false
    for ($i = 1; $i -le 15; $i++) {
        Start-Sleep -Seconds 2
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "✅  Ollama is ready (attempt $i/15)." -ForegroundColor Green
                $ready = $true
                break
            }
        } catch {
            # Not ready yet
        }
    }
    if (-not $ready) {
        Write-Host "❌  Ollama failed to start within 30 seconds." -ForegroundColor Red
        exit 1
    }
}

# ── Step 3: Pull the Llama3 model ────────────────────────────────────────────
$model = if ($env:OLLAMA_MODEL_NAME) { $env:OLLAMA_MODEL_NAME } else { "llama3" }
Write-Host "▶  Pulling model: $model" -ForegroundColor Yellow
Write-Host "   (First run downloads ~4.7 GB — may take several minutes)" -ForegroundColor Gray
& ollama pull $model
Write-Host "✅  Model ready: $model" -ForegroundColor Green

# ── Step 4: Configure environment ─────────────────────────────────────────────
$backendDir = Join-Path $PSScriptRoot "..\backend"
Push-Location $backendDir

if (-not (Test-Path ".env")) {
    Write-Host "▶  Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

$env:LLM_PROVIDER = "ollama"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_MODEL_NAME = $model

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "▶  Starting PsyPredict Backend (Ollama mode)" -ForegroundColor Yellow
Write-Host "   LLM_PROVIDER=$($env:LLM_PROVIDER)" -ForegroundColor Gray
Write-Host "   OLLAMA_BASE_URL=$($env:OLLAMA_BASE_URL)" -ForegroundColor Gray
Write-Host "   OLLAMA_MODEL_NAME=$($env:OLLAMA_MODEL_NAME)" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan

# ── Step 5: Start the backend ─────────────────────────────────────────────────
& uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload --log-level info

Pop-Location
