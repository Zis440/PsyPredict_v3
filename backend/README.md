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
| LLM Inference | Llama 3.3 70B via Groq API (free, ~2–3 sec) |
| Text Emotion | DistilBERT (`bhadresh-savani/distilbert-base-uncased-emotion`) |
| Crisis Detection | Zero-shot NLI (MiniLM) |
| Face Emotion | Keras CNN (custom trained, `emotion_model_trained.h5`) |
| Remedies | CSV lookup (`MEDICATION.csv`) + Gita wisdom |

## A Note on `ollama_engine.py`

The LLM engine is named `ollama_engine.py` for historical compatibility — Ollama is
the framework that runs Llama models. The current implementation calls **Groq's hosted
API** (`api.groq.com`) using the OpenAI-compatible `/chat/completions` endpoint, which
serves the same Llama 3.3 70B model on Groq's custom LPU hardware. No Ollama binary
is installed in the container. See `OLLAMA_VPS_GUIDE.md` at the project root if you
want to switch to a self-hosted Ollama instance.

## Required Secrets (HF Spaces → Settings → Variables and Secrets)

| Key | Type | Description |
|-----|------|-------------|
| `GROQ_API_KEY` | **Secret** | From console.groq.com (free) |
| `GROQ_MODEL` | Variable | `llama-3.3-70b-versatile` |
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

## Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up config
copy .env.example .env
# Edit .env → add GROQ_API_KEY=gsk_...

# 3. Start server
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

Swagger docs: http://localhost:7860/docs

## Key Files

```
app/
├── main.py                   # FastAPI app factory + lifespan
├── config.py                 # Pydantic Settings (GROQ_API_KEY, GROQ_MODEL, etc.)
├── schemas.py                # All request/response models (PsychReport etc.)
├── services/
│   ├── ollama_engine.py      # Groq/Llama3.3 async client (named for compatibility)
│   ├── text_emotion_engine.py# DistilBERT classifier
│   ├── crisis_engine.py      # Zero-shot NLI crisis detection
│   ├── fusion_engine.py      # Multimodal weighted fusion
│   ├── emotion_engine.py     # Keras CNN face emotion
│   └── remedy_engine.py      # CSV remedy lookup
└── api/endpoints/
    ├── therapist.py          # POST /api/chat
    ├── facial.py             # POST /api/predict/emotion
    ├── remedies.py           # GET  /api/get_advice
    └── analysis.py           # POST /api/analyze/text + GET /api/health
```
