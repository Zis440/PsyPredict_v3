---
title: PsyPredict Backend
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# PsyPredict Backend

**FastAPI** backend for PsyPredict — production-grade multimodal clinical AI system.

## What Runs Here

| Service | Technology |
|---------|-----------|
| API Framework | FastAPI + Uvicorn |
| LLM Inference | Ollama / Phi 3.5 Mini (local) |
| Text Emotion | DistilBERT (`bhadresh-savani/distilbert-base-uncased-emotion`) |
| Crisis Detection | Zero-shot NLI (MiniLM) |
| Face Emotion | Keras CNN (custom trained, `emotion_model_trained.h5`) |
| Remedies | CSV lookup (`MEDICATION.csv`) |

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Main therapist — returns `PsychReport` |
| `POST` | `/api/predict/emotion` | Facial emotion detection |
| `GET`  | `/api/get_advice` | Remedy/condition lookup |
| `POST` | `/api/analyze/text` | Text emotion + crisis score |
| `GET`  | `/api/health` | System health check |

## Running Locally

```bash
# 1. Install Ollama + LLaMA 3 (one-time)
winget install Ollama.Ollama
ollama pull phi3.5:3.8b-mini-instruct-q4_0

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

Swagger docs: http://localhost:7860/docs

## Key Files

```
app/
├── main.py                   # FastAPI app factory
├── config.py                 # Pydantic Settings
├── schemas.py                # All request/response models (PsychReport etc.)
├── services/
│   ├── ollama_engine.py      # LLaMA 3 async client
│   ├── text_emotion_engine.py# DistilBERT classifier
│   ├── crisis_engine.py      # Zero-shot NLI crisis detection
│   ├── fusion_engine.py      # Multimodal weighted fusion
│   ├── emotion_engine.py     # Keras CNN face emotion (preserved)
│   └── remedy_engine.py      # CSV remedy lookup (preserved)
└── api/endpoints/
    ├── therapist.py          # POST /api/chat
    ├── facial.py             # POST /api/predict/emotion
    ├── remedies.py           # GET  /api/get_advice
    └── analysis.py           # POST /api/analyze/text + GET /api/health
```
