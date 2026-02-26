# PsyPredict — Quick Start

## Prerequisites (one-time)

```
winget install Ollama.Ollama
ollama pull llama3
```

---

## Terminal 1 — Backend

```
cd backend
venv\Scripts\Activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

API docs (Swagger): http://localhost:7860/docs

---

## Terminal 2 — Frontend

```
cd frontend
npm run dev
```

App: http://localhost:5173

---

## Terminal 3 — Ollama (keep running)

```
ollama serve
```