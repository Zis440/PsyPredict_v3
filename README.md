# 🧠 PsyPredict
> *Production-Grade Multimodal Clinical AI System*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/backend-FastAPI-009688.svg)
![React](https://img.shields.io/badge/frontend-React-cyan.svg)
![Llama3](https://img.shields.io/badge/LLM-Llama3.3--70B%20%28Groq%29-indigo.svg)
![Vercel](https://img.shields.io/badge/frontend-Vercel-black)

---

## Overview

**PsyPredict** is a fully production-grade multimodal mental health AI system. It combines:

- **DistilBERT** multi-label text emotion classification
- **Llama 3.3 70B** via Groq API for structured clinical reasoning (free, ~2–3 sec response)
- **Keras CNN** facial emotion detection (live webcam)
- **Zero-shot NLI** crisis detection with automatic override
- **Weighted multimodal fusion** for a combined distress risk score
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

### 3. Crisis Detection Layer
- Zero-shot NLI classification across 5 risk dimensions (NOT keyword matching)
- Weighted risk scoring — triggers at configurable threshold (default: 0.65)
- **Overrides LLM** — deterministic crisis response with emergency hotlines (iCall, Vandrevala, AASRA)

### 4. Bhagavad Gita Remedy System
- CSV-based remedy lookup matched to detected risk level
- Gita wisdom quote + medications + dosage + recommended treatments
- Displayed as a collapsible panel alongside the clinical report

### 5. Production Hardened
- Input sanitization (HTML strip, 2000-char limit)
- Retry with exponential backoff on Groq failures
- Graceful fallback when Groq API key missing or unreachable
- Rate limiting (30 req/min)
- Structured logging
- Pydantic validation on all I/O
- Context window trimming (last 10 turns)

---

## System Architecture

```
User Text Input
      │
      ├─► DistilBERT Text Emotion Classifier
      │       └─► emotion labels + confidence
      │
      ├─► Crisis Engine (Zero-Shot NLI)
      │       └─► weighted risk score
      │               ├─ score ≥ 0.65 → CRISIS OVERRIDE (no LLM)
      │               └─ ELSE → continue
      │
      ├─► Multimodal Fusion Engine
      │       ├─ text_distress × 0.65
      │       └─ face_distress × 0.35 → final_risk_score
      │
      └─► Groq API → Llama 3.3 70B (structured JSON via ---JSON--- marker)
              └─► PsychReport (Pydantic validated)
                      └─► Remedy lookup (CSV → Gita + medication panel)

Webcam → Keras CNN → face emotion score → Fusion Engine
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React, Vite, TypeScript, TailwindCSS |
| **Backend** | Python, FastAPI, Uvicorn |
| **LLM** | Llama 3.3 70B via Groq API (free tier, ~2–3 sec) |
| **Text Emotion** | DistilBERT (`bhadresh-savani/distilbert-base-uncased-emotion`) |
| **Crisis Detection** | MiniLM Zero-Shot NLI |
| **Face Emotion** | OpenCV + Custom Keras CNN |
| **Database & Auth** | Convex (auth + conversation history) |
| **Remedies** | Pandas + CSV knowledge base |
| **Hosting** | HF Spaces (backend) · Vercel (frontend) |

---

## Folder Structure

```
PsyPredict/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app + lifespan
│   │   ├── config.py                  # Pydantic Settings (GROQ_API_KEY etc.)
│   │   ├── schemas.py                 # PsychReport + all API models
│   │   ├── ml_assets/
│   │   │   ├── emotion_model_trained.h5
│   │   │   ├── haarcascade_frontalface_default.xml
│   │   │   └── MEDICATION.csv
│   │   ├── services/
│   │   │   ├── ollama_engine.py       # Groq/Llama3.3 async client (named for compatibility)
│   │   │   ├── text_emotion_engine.py # DistilBERT text emotion
│   │   │   ├── crisis_engine.py       # Zero-shot NLI crisis detection
│   │   │   ├── fusion_engine.py       # Multimodal weighted fusion
│   │   │   ├── emotion_engine.py      # Keras CNN face emotion
│   │   │   └── remedy_engine.py       # CSV remedy lookup
│   │   └── api/endpoints/
│   │       ├── therapist.py           # POST /api/chat
│   │       ├── facial.py              # POST /api/predict/emotion
│   │       ├── remedies.py            # GET  /api/get_advice
│   │       └── analysis.py            # POST /api/analyze/text
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/features/
│   │   │   ├── ChatInterface.tsx      # Chat + combined Clinical+Remedy panel
│   │   │   ├── WebcamFeed.tsx         # Live webcam emotion feed
│   │   │   └── RemedyCard.tsx         # Standalone Gita remedy card
│   │   ├── services/api.ts            # Typed API client
│   │   └── pages/
│   │       ├── Dashboard.tsx
│   │       └── History.tsx
│   └── package.json
├── DEPLOY.md                          # Full deployment guide
├── OLLAMA_VPS_GUIDE.md               # Self-hosted Ollama fallback guide
└── INSTRUCTIONS.md
```

---

## Getting Started (Local Development)

### Backend Setup

```bash
cd backend

# Create and activate virtualenv
python -m venv venv
venv\Scripts\Activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy config and add your Groq API key
copy .env.example .env
# Edit .env → set GROQ_API_KEY=gsk_...

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

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

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Full clinical pipeline → `PsychReport` |
| `POST` | `/api/predict/emotion` | Facial emotion detection |
| `GET`  | `/api/get_advice?condition=` | Remedy lookup |
| `POST` | `/api/analyze/text` | Text emotion + crisis pre-screen |
| `GET`  | `/api/health` | System health check |

---

## Configuration (`.env`)

```env
# ── Groq API (LLM inference) ──────────────────────────────────────────────
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# ── ML Models ─────────────────────────────────────────────────────────────
DISTILBERT_MODEL=bhadresh-savani/distilbert-base-uncased-emotion
CRISIS_THRESHOLD=0.65

# ── Fusion Weights ────────────────────────────────────────────────────────
TEXT_WEIGHT=0.65
FACE_WEIGHT=0.35

# ── App ───────────────────────────────────────────────────────────────────
MAX_CONTEXT_TURNS=10
LOG_LEVEL=INFO
RATE_LIMIT=30/minute
```

---

## Deployment

| Layer | Platform | Notes |
|---|---|---|
| **Frontend** | Vercel | Auto-deploys from GitHub |
| **Backend** | Hugging Face Spaces | Docker SDK, free tier |
| **LLM** | Groq API | Free tier, no infrastructure needed |

See `DEPLOY.md` for the full step-by-step deployment guide.

---

## A Note on the LLM Layer

The inference engine (`services/ollama_engine.py`) is named after Ollama — the framework
that originally ran Llama models locally. The current setup routes requests to **Groq's
hosted API** instead, which runs the same Llama 3.3 70B model on their custom LPU hardware.
The result is identical model behaviour at ~2–3 second response times with no self-hosted
infrastructure required. If you ever want to switch back to a self-hosted Ollama instance,
see `OLLAMA_VPS_GUIDE.md`.

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
