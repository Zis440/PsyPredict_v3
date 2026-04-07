# 🧠 PsyPredict
> *Production-Grade Multimodal Clinical AI System*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/backend-FastAPI-009688.svg)
![React](https://img.shields.io/badge/frontend-React-cyan.svg)
![Llama3](https://img.shields.io/badge/LLM-Llama3%20%28Groq%20%7C%20Ollama%29-indigo.svg)
![Vercel](https://img.shields.io/badge/frontend-Vercel-black)

---

## Overview

**PsyPredict** is a fully production-grade multimodal mental health AI system. It combines :

- **DistilBERT** multi-label text emotion classification
- **Llama 3** via **Groq API** (cloud, default) or **Ollama** (local) for structured clinical reasoning
- **Keras CNN** facial emotion detection (live webcam)
- **Zero-shot NLI** crisis detection with automatic override
- **Weighted multimodal fusion** for a combined distress risk score
- **FAISS semantic knowledge index** for contextually relevant Gita wisdom and remedies
- **Adaptive patient memory** (SQLite or Supabase) that personalizes responses over time
- **Bhagavad Gita** remedy system — culturally grounded guidance from CSV knowledge base

Every AI response returns a structured **PsychReport** — not a generic chatbot reply.

---

## Key Features

### 1. Multimodal Emotion Understanding
- **Facial Analysis:** Keras CNN detects live emotions via webcam (7 classes)
- **Text Analysis:** DistilBERT classifies multi-label emotions from user text
- **Weighted Fusion:** `(Text × 0.65) + (Face × 0.35)` → unified distress score

### 2. Clinical-Grade Output (PsychReport)
Every chat response includes:
- `risk_classification` — MINIMAL / LOW / MODERATE / HIGH / CRITICAL
- `emotional_state_summary` — concise, grounded assessment
- `behavioral_inference` — inferred patterns from conversation
- `cognitive_distortions` — CBT distortion labels detected
- `suggested_interventions` — clinically actionable recommendations
- `confidence_score` — LLM self-assessed confidence
- `routing` — which LLM provider handled the request and why

### 3. Crisis Detection Layer
- Zero-shot NLI classification across 5 risk dimensions (NOT keyword matching)
- Weighted risk scoring — triggers at configurable threshold (default: 0.65)
- **Overrides LLM** — deterministic crisis response with emergency hotlines (iCall, Vandrevala, AASRA)

### 4. Dual-LLM Orchestration
- Clean provider abstraction (`BaseLLMClient`) — Groq and Ollama share identical interfaces
- Intelligent routing: task type, privacy sensitivity, and provider availability all influence which provider handles each request
- PII scrubbing before any cloud call — sensitive data never leaves the local machine when using Ollama
- Automatic fallback: if the primary provider is down, the secondary is tried seamlessly
- Zero config for HF Spaces — `LLM_PROVIDER` defaults to `"groq"`, no disruption to cloud deployment

### 5. Adaptive Patient Memory
- Per-patient session history stored in SQLite (local, zero-config) or Supabase (cloud)
- Preferences system: each patient can have a preferred tone, verbosity level, and therapy framework
- The LLM prompt adapts dynamically based on past sessions, risk trends, and feedback ratings
- Background session summarization runs after each chat turn

### 6. FAISS Semantic Knowledge Index
- Embeds the Gita wisdom + remedy dataset using `sentence-transformers/all-MiniLM-L6-v2`
- Retrieves the most semantically relevant shloka and condition for each user message
- Falls back to exact-match CSV lookup if the index is not yet ready

### 7. Bhagavad Gita Remedy System
- Semantically matched remedy lookup (FAISS) with exact-match CSV fallback
- Gita wisdom quote + medications + dosage + recommended treatments
- Displayed as a collapsible panel alongside the clinical report

### 8. Production Hardened
- Input sanitization (HTML strip, 2000-char limit, Pydantic validation)
- Retry with exponential backoff on all LLM provider failures
- Graceful fallback — server never crashes due to LLM issues
- Rate limiting (30 req/min per IP via SlowAPI)
- Structured logging with request-level routing metadata
- PII scrubbing layer before any cloud LLM call
- Context window trimming (last 10 turns)
- Dual-LLM orchestration with automatic fallback (Ollama ↔ Groq)
- PII scrubbing before any cloud LLM call (regex-based, zero ML dependencies)
- Adaptive patient memory — SQLite or Supabase backend, configurable
- FAISS semantic knowledge retrieval for Gita context
- Background session summarization (fire-and-forget async)
- Patient progress tracking across sessions

---

## System Architecture

### Pipeline
![Pipeline Architecture](docs/pipeline.png)

### Application Workflow
![Application Workflow](docs/workflow.png)

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React, Vite, TypeScript, TailwindCSS |
| **Backend** | Python, FastAPI, Uvicorn |
| **LLM (cloud)** | Llama 3.3 70B via Groq API (default for HF Spaces) |
| **LLM (local)** | Llama 3 via Ollama (local development) |
| **Text Emotion** | DistilBERT (`bhadresh-savani/distilbert-base-uncased-emotion`) |
| **Crisis Detection** | MiniLM Zero-Shot NLI |
| **Face Emotion** | OpenCV + Custom Keras CNN |
| **Semantic Search** | FAISS + `sentence-transformers/all-MiniLM-L6-v2` |
| **Database** | SQLite (patient memory, default) · Supabase (optional cloud) · Convex (frontend history) |
| **Auth** | Clerk |
| **Remedies** | Pandas + CSV knowledge base |
| **Hosting** | HF Spaces (backend) · Vercel (frontend) |

---

## Folder Structure

```
PsyPredict/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app factory + lifespan
│   │   ├── config.py                    # Pydantic Settings (all env vars)
│   │   ├── schemas.py                   # PsychReport + all API models
│   │   ├── ml_assets/
│   │   │   ├── emotion_model_trained.h5
│   │   │   ├── haarcascade_frontalface_default.xml
│   │   │   └── MEDICATION.csv
│   │   ├── services/
│   │   │   ├── base_llm_client.py       # Abstract LLM interface (BaseLLMClient)
│   │   │   ├── groq_client.py           # Groq cloud API client
│   │   │   ├── ollama_client.py         # Ollama local HTTP client
│   │   │   ├── llm_provider.py          # Factory — resolves LLM_PROVIDER to a client
│   │   │   ├── llm_shared.py            # Shared prompt, parsing, adaptive system prompt
│   │   │   ├── llm_orchestrator.py      # Dual-LLM routing engine (task/PII/fallback logic)
│   │   │   ├── ollama_engine.py         # Backwards-compatible shim (delegates to factory)
│   │   │   ├── pii_scrubber.py          # PII redaction before cloud calls
│   │   │   ├── text_emotion_engine.py   # DistilBERT text emotion classifier
│   │   │   ├── crisis_engine.py         # Zero-shot NLI crisis detection
│   │   │   ├── fusion_engine.py         # Multimodal weighted fusion
│   │   │   ├── emotion_engine.py        # Keras CNN face emotion
│   │   │   ├── remedy_engine.py         # CSV remedy lookup
│   │   │   ├── knowledge_index.py       # FAISS semantic knowledge index
│   │   │   ├── patient_memory.py        # Adaptive patient memory (SQLite / Supabase)
│   │   │   ├── session_summarizer.py    # Background session summarization
│   │   │   └── progress_tracker.py      # Patient progress tracking over time
│   │   └── api/endpoints/
│   │       ├── therapist.py             # POST /api/chat
│   │       ├── facial.py               # POST /api/predict/emotion
│   │       ├── remedies.py             # GET  /api/get_advice
│   │       ├── analysis.py             # POST /api/analyze/text · GET /api/health · GET /api/llm/status
│   │       ├── progress.py             # GET  /api/progress · POST /api/feedback
│   │       └── orchestrator_status.py  # GET  /api/orchestrator/status · logs · refresh
│   ├── tests/
│   │   ├── test_llm_clients.py         # Unit tests (mocked — no provider needed)
│   │   └── test_manual_providers.py    # Manual integration test (live provider)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── start.sh                        # Entrypoint (starts Ollama + FastAPI)
│   ├── download_models.py              # Pre-warms ML assets at build time
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/features/
│   │   │   ├── ChatInterface.tsx       # Chat + Clinical + Remedy panel
│   │   │   ├── WebcamFeed.tsx          # Live webcam emotion feed
│   │   │   └── RemedyCard.tsx          # Gita remedy card
│   │   ├── services/api.ts             # Typed API client
│   │   └── pages/
│   │       ├── Dashboard.tsx
│   │       └── History.tsx
│   └── package.json
├── scripts/
│   ├── local_setup.sh                  # macOS/Linux quick-start (Ollama + backend)
│   └── local_setup.ps1                 # Windows PowerShell quick-start
├── docs/
│   ├── DEPLOY.md                       # Full cloud deployment guide
│   ├── OLLAMA_VPS_GUIDE.md             # Self-hosted Ollama on VPS/EC2
│   ├── PIPELINE_ARCHITECTURE_GUIDE.md
│   └── WORKFLOW_ARCHITECTURE_GUIDE.md
├── docker-compose.yml                  # Local dev: Ollama + Backend + Frontend
├── INSTRUCTIONS.md
└── README.md
```

---

## Getting Started (Local Development)

### Backend Setup (Ollama — No API Key Needed)

```bash
# 1. Install Ollama from https://ollama.com/download
ollama serve              # Start the server
ollama pull llama3        # Download the model (~4.7 GB)

cd backend

# 2. Create and activate virtualenv
python -m venv venv
venv\Scripts\Activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up config
copy .env.example .env
# Edit .env → set LLM_PROVIDER=ollama

# 5. Start backend
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

> **Quick start scripts** in `scripts/` handle all of the above automatically:
> ```bash
> ./scripts/local_setup.sh        # macOS / Linux
> .\scripts\local_setup.ps1       # Windows PowerShell
> ```

> **Using Groq instead?** Set `LLM_PROVIDER=groq` and `GROQ_API_KEY=gsk_...` in `.env`.

Swagger UI: **http://localhost:7860/docs**

### Frontend Setup

```bash
cd frontend
npm install

# Start Convex dev server (in one terminal)
npx convex dev

# Start frontend (in another terminal)
npm run dev
```

App: **http://localhost:5173**

### Full Stack with Docker Compose

```bash
# From the project root — starts Ollama + Backend + Frontend together
docker compose up --build
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Full clinical pipeline → `PsychReport` + routing metadata |
| `POST` | `/api/predict/emotion` | Facial emotion detection |
| `GET`  | `/api/get_advice?condition=` | Remedy lookup |
| `POST` | `/api/analyze/text` | Text emotion + crisis pre-screen |
| `GET`  | `/api/health` | System health (both LLM providers, DistilBERT, FAISS) |
| `GET`  | `/api/llm/status` | LLM provider status (provider, model, reachability, fallback) |
| `GET`  | `/api/orchestrator/status` | Orchestrator routing stats (requests, latency, PII scrubs) |
| `GET`  | `/api/orchestrator/logs` | Recent routing decisions |
| `POST` | `/api/orchestrator/refresh` | Re-check both providers' health without restart |
| `GET`  | `/api/progress/{user_id}` | Patient progress over sessions |
| `POST` | `/api/feedback` | Submit session feedback (1–5 rating) |

---

## Configuration (`.env`)

```env
# ── LLM Provider ──────────────────────────────────────────────────────────
LLM_PROVIDER=ollama            # "groq" (cloud) or "ollama" (local)

# ── Groq API (when LLM_PROVIDER=groq) ────────────────────────────────────
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# ── Ollama (when LLM_PROVIDER=ollama) ────────────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama3
OLLAMA_TIMEOUT_S=120
OLLAMA_RETRIES=3

# ── ML Models ─────────────────────────────────────────────────────────────
DISTILBERT_MODEL=bhadresh-savani/distilbert-base-uncased-emotion
CRISIS_THRESHOLD=0.65

# ── Fusion Weights ────────────────────────────────────────────────────────
TEXT_WEIGHT=0.65
FACE_WEIGHT=0.35

# ── Patient Memory ────────────────────────────────────────────────────────
PATIENT_MEMORY_BACKEND=sqlite  # or "supabase"

# ── App ───────────────────────────────────────────────────────────────────
MAX_CONTEXT_TURNS=10
LOG_LEVEL=INFO
RATE_LIMIT=30/minute
```

See `backend/.env.example` for the complete list with descriptions.

---

## Deployment

| Layer | Platform | Notes |
|---|---|---|
| **Frontend** | Vercel | Auto-deploys from GitHub |
| **Backend** | Hugging Face Spaces | Docker SDK, free tier |
| **LLM** | Groq API (cloud default) / Ollama (local) | Configurable via `LLM_PROVIDER` |

See `docs/DEPLOY.md` for the full step-by-step deployment guide.

---

## Testing

```bash
cd backend

# Unit tests (mocked — no provider or server needed)
pytest tests/test_llm_clients.py -v

# Manual integration test — test one provider
LLM_PROVIDER=ollama python tests/test_manual_providers.py
LLM_PROVIDER=groq   python tests/test_manual_providers.py

# Compare both providers side by side
python tests/test_manual_providers.py --both
```

---

## Disclaimer

> This system is a **clinical decision-support tool** for emotional support and educational
> purposes only. It does **not** provide medical diagnosis or professional therapy. If you
> or someone you know is in crisis, please contact emergency services or a licensed mental
> health professional immediately.
>
> **India crisis lines:** iCall: 9152987821 | Vandrevala: 1860-2662-345 | AASRA: 9820466627

---

## License

MIT License — see [LICENSE](./LICENSE)

---

Built by [@Zis440](https://github.com/Zis440), [@therandomuser03](https://github.com/therandomuser03) & [@SanjanaChatterjee](https://github.com/SanjanaChatterjee)
