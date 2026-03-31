---
title: PsyPredict [Backend]
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# PsyPredict — Backend

**FastAPI** backend for PsyPredict — production-grade multimodal clinical AI system.

## What Runs Here

| Service | Technology |
|---------|-----------|
| API Framework | FastAPI + Uvicorn (port 7860) |
| LLM Inference | **Groq** (cloud, default) or **Ollama** (local) — configurable via `LLM_PROVIDER` |
| Text Emotion | DistilBERT (`bhadresh-savani/distilbert-base-uncased-emotion`) |
| Crisis Detection | Zero-shot NLI (MiniLM) |
| Face Emotion | Keras CNN (custom trained, `emotion_model_trained.h5`) |
| Remedies | CSV lookup (`MEDICATION.csv`) + Gita wisdom |

## LLM Provider Architecture

The backend supports **two LLM providers** via a clean abstraction layer:

| Provider | Use Case | Config |
|----------|----------|--------|
| **Groq** (default) | Cloud deployment (HF Spaces) | `LLM_PROVIDER=groq` + `GROQ_API_KEY` |
| **Ollama** | Local development | `LLM_PROVIDER=ollama` — no API key needed |

Both providers share identical prompt construction, response parsing, and PsychReport schema. Switching is seamless — just change the env var.

### Key Files

```
app/services/
├── base_llm_client.py   # Abstract interface (BaseLLMClient)
├── groq_client.py       # Groq API client (OpenAI-compatible)
├── ollama_client.py     # Ollama HTTP client (local)
├── llm_provider.py      # Factory — picks the right client
├── llm_shared.py        # Shared prompt, parsing, constants
└── ollama_engine.py     # Backwards-compatible shim (delegates to factory)
```

## Required Secrets (HF Spaces → Settings → Variables and Secrets)

| Key | Type | Description |
|-----|------|-------------|
| `GROQ_API_KEY` | **Secret** | From console.groq.com (free) |
| `GROQ_MODEL` | Variable | `llama-3.3-70b-versatile` |
| `LLM_PROVIDER` | Variable | `groq` (or leave unset — defaults to `groq`) |
| `CRISIS_THRESHOLD` | Variable | `0.65` |
| `LOG_LEVEL` | Variable | `INFO` |
| `RATE_LIMIT` | Variable | `30/minute` |

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Main therapist — returns `PsychReport` + remedy |
| `POST` | `/api/predict/emotion` | Facial emotion detection |
| `GET`  | `/api/get_advice` | Remedy/condition lookup (Gita + medication) |
| `POST` | `/api/analyze/text` | Text emotion + crisis score |
| `GET`  | `/api/health` | System health check |
| `GET`  | `/api/llm/status` | LLM provider status (provider, reachability, model) |

## Running Locally (with Ollama)

### Option A: Quick Setup Script (Recommended)

```powershell
# Windows PowerShell
.\scripts\local_setup.ps1
```

```bash
# macOS / Linux
chmod +x scripts/local_setup.sh
./scripts/local_setup.sh
```

The script will: install check Ollama → start the server → pull llama3 → launch the backend.

### Option B: Manual Setup

```bash
# 1. Install & start Ollama (https://ollama.com/download)
ollama serve          # Start the server
ollama pull llama3    # Download the model (~4.7 GB)

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set up config
copy .env.example .env
# Edit .env → set LLM_PROVIDER=ollama

# 4. Start server
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

### Option C: Docker Compose

```bash
# From the project root (starts Ollama + Backend + Frontend)
docker compose up --build
```

### Running with Groq (Cloud)

```bash
# Edit .env → set:
#   LLM_PROVIDER=groq
#   GROQ_API_KEY=gsk_your_key_here

uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

Swagger docs: http://localhost:7860/docs

## Testing

```bash
# Unit tests (mocked, no LLM server needed)
pytest tests/test_llm_clients.py -v

# Manual integration test (needs running provider)
LLM_PROVIDER=ollama python tests/test_manual_providers.py

# Test both providers side by side
python tests/test_manual_providers.py --both
```

## Full File Structure

```
app/
├── main.py                   # FastAPI app factory + lifespan
├── config.py                 # Pydantic Settings (LLM_PROVIDER, GROQ_*, OLLAMA_*, etc.)
├── schemas.py                # All request/response models (PsychReport, LLMStatusResponse, etc.)
├── services/
│   ├── base_llm_client.py    # Abstract LLM client interface
│   ├── groq_client.py        # Groq cloud API client
│   ├── ollama_client.py      # Ollama local HTTP client
│   ├── llm_provider.py       # Factory — resolves LLM_PROVIDER to a client
│   ├── llm_shared.py         # Shared prompt, parsing, constants
│   ├── ollama_engine.py      # Backwards-compatible shim
│   ├── text_emotion_engine.py# DistilBERT classifier
│   ├── crisis_engine.py      # Zero-shot NLI crisis detection
│   ├── fusion_engine.py      # Multimodal weighted fusion
│   ├── emotion_engine.py     # Keras CNN face emotion
│   ├── remedy_engine.py      # CSV remedy lookup
│   └── patient_memory.py     # Adaptive learning memory
└── api/endpoints/
    ├── therapist.py          # POST /api/chat
    ├── facial.py             # POST /api/predict/emotion
    ├── remedies.py           # GET  /api/get_advice
    └── analysis.py           # POST /api/analyze/text + health + llm/status
```
