# 🧠 PsyPredict v2.0
> *Production-Grade Multimodal Clinical AI System*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/backend-FastAPI-009688.svg)
![React](https://img.shields.io/badge/frontend-React-cyan.svg)
![LLaMA](https://img.shields.io/badge/LLM-LLaMA%203%20%28Ollama%29-orange.svg)
![Vercel](https://img.shields.io/badge/frontend-Vercel-black)

---

## Overview

**PsyPredict v2.0** is a fully local, production-grade multimodal mental health AI system. It combines:

- **DistilBERT** multi-label text emotion classification
- **LLaMA 3** via Ollama for structured clinical reasoning (no external API)
- **Keras CNN** facial emotion detection (live webcam)
- **Zero-shot NLI** crisis detection with automatic override
- **Weighted multimodal fusion** for a combined distress risk score

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
- CSV-based remedy lookup for mental conditions
- Culturally grounded story-based guidance

### 5. Production Hardened
- Input sanitization (HTML strip, 2000-char limit)
- Retry with exponential backoff on Ollama failures
- Graceful fallback when Ollama unreachable
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
      └─► Ollama / LLaMA 3 (local, structured JSON)
              └─► PsychReport (Pydantic validated)

Webcam → Keras CNN → face emotion score → Fusion Engine
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React, Vite, TypeScript, TailwindCSS |
| **Backend** | Python, FastAPI, Uvicorn |
| **LLM** | LLaMA 3 via Ollama (local, no external API) |
| **Text Emotion** | DistilBERT (`bhadresh-savani/distilbert-base-uncased-emotion`) |
| **Crisis Detection** | MiniLM Zero-Shot NLI |
| **Face Emotion** | OpenCV + Custom Keras CNN |
| **Database** | Supabase (conversation history) |
| **Remedies** | Pandas + CSV knowledge base |

---

## Folder Structure

```
PsyPredict/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app + lifespan
│   │   ├── config.py                  # Pydantic Settings
│   │   ├── schemas.py                 # PsychReport + all API models
│   │   ├── ml_assets/
│   │   │   ├── emotion_model_trained.h5
│   │   │   ├── haarcascade_frontalface_default.xml
│   │   │   └── MEDICATION.csv
│   │   ├── services/
│   │   │   ├── ollama_engine.py       # LLaMA 3 async client
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
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/features/
│   │   │   ├── ChatInterface.tsx      # Chat + Clinical Report panel
│   │   │   ├── WebcamFeed.tsx         # Live webcam emotion feed
│   │   │   └── RemedyCard.tsx         # Gita remedy display
│   │   ├── services/api.ts            # Typed API client
│   │   └── pages/
│   │       ├── Dashboard.tsx
│   │       └── History.tsx
│   └── package.json
└── TO RUN .md
```

---

## Getting Started

### Prerequisites (one-time)

```bash
# Install Ollama
winget install Ollama.Ollama   # Windows
# or: brew install ollama       # macOS

# Pull LLaMA 3 model (~4.7 GB)
ollama pull llama3

# Verify
ollama list
```

### Backend Setup

```bash
cd backend

# Activate virtualenv (recommended)
python -m venv venv
venv\Scripts\Activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies (DistilBERT auto-downloads ~250 MB on first run)
pip install -r requirements.txt

# Copy and review config
copy .env.example .env

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

Swagger UI: **http://localhost:7860/docs**

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App: **http://localhost:5173**

### Keep Ollama Running

```bash
# In a separate terminal (if not running as a service)
ollama serve
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Full clinical pipeline → `PsychReport` |
| `POST` | `/api/predict/emotion` | Facial emotion detection |
| `GET`  | `/api/get_advice?condition=` | Remedy lookup |
| `POST` | `/api/analyze/text` | Text emotion + crisis pre-screen |
| `GET`  | `/api/health` | System health (Ollama + DistilBERT) |

---

## Configuration (`.env`)

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_TIMEOUT_S=90
DISTILBERT_MODEL=bhadresh-savani/distilbert-base-uncased-emotion
CRISIS_THRESHOLD=0.65
TEXT_WEIGHT=0.65
FACE_WEIGHT=0.35
MAX_CONTEXT_TURNS=10
LOG_LEVEL=INFO
RATE_LIMIT=30/minute
```

---

## Deployment

- **Frontend:** [Vercel](https://psypredict.vercel.app)
- **Backend (v2.0):** Requires a machine with Ollama installed — Hugging Face Spaces or any VM with Docker + GPU recommended

---

## Disclaimer

> This system is a **clinical decision-support tool** for emotional support and educational purposes only. It does **not** provide medical diagnosis or professional therapy. If you or someone you know is in crisis, please contact emergency services or a licensed mental health professional immediately.
>
> **India crisis lines:** iCall: 9152987821 | Vandrevala: 1860-2662-345 | AASRA: 9820466627

---

## License

MIT License — see [LICENSE](./LICENSE)
