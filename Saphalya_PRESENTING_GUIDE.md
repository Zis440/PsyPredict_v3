# 🎤 PsyPredict v2.0 — Complete Presentation Guide

> **Prepared for: Saphalya**
> **Date: March 2026**
> **Project: PsyPredict — Production-Grade Multimodal Clinical AI System**

---

# 📑 PART 1 — PPT PRESENTATION GUIDE

> Use this section as a **slide-by-slide script** for your PowerPoint / Google Slides presentation.

---

## SLIDE 1 — Title Slide

**Title:** *PsyPredict v2.0 — AI-Powered Multimodal Mental Health Analysis*

**Subtitle:** A fully local, privacy-first clinical AI system for real-time emotional assessment

**Visuals:** Project logo / clean dark gradient background with neural-network mesh art

**Talking Points:**
- Introduce yourself: name, role, institution
- One-liner: *"PsyPredict uses four AI models working together to understand how someone is feeling — from their words, their face, and the clinical danger signals in between."*

---

## SLIDE 2 — The Problem

**Title:** *The Mental Health Gap*

**Key Stats to Display:**
- 1 in 8 people globally live with a mental disorder (WHO, 2022)
- India has < 1 psychiatrist per 100,000 people
- 70%+ of mental health conditions go undiagnosed
- Crisis detection is still keyword-based in most apps — dangerously unreliable

**Talking Points:**
- Mental health screening is slow, inaccessible, and often missed
- Most mental health apps use basic sentiment analysis — no clinical depth
- Crisis detection based on keywords like "suicide" misses nuanced distress signals
- There is a **massive gap** between what AI can do and what mental health tools actually do today

---

## SLIDE 3 — Our Solution

**Title:** *PsyPredict — What It Does*

**Bullet Points:**
1. **Multimodal Analysis** — Understands emotions from text AND facial expressions simultaneously
2. **Clinical-Grade Reports** — Every response returns a structured `PsychReport`, not a chatbot reply
3. **Crisis Safety Net** — Zero-shot AI crisis detection that overrides the system when danger is detected
4. **Fully Local** — All AI runs on your machine. No data leaves. No cloud APIs.
5. **Culturally Grounded** — Includes Bhagavad Gita–based remedies for holistic guidance

**Talking Points:**
- This is NOT a chatbot. It's a clinical decision-support system that produces structured psychological assessments
- Every single response is validated through Pydantic schemas — no hallucinated junk
- The crisis layer runs BEFORE the LLM — if someone is in danger, the system responds immediately with helpline numbers

---

## SLIDE 4 — System Architecture

**Title:** *How It Works — Architecture Overview*

**Visual:** Display the architecture diagram (use `DOCUMENTATION/PIPELINE.PNG` or recreate)

```
User Text Input
      │
      ├─► DistilBERT Text Emotion Classifier
      │       └─► emotion labels + confidence
      │
      ├─► Crisis Engine (Zero-Shot NLI)
      │       └─► weighted risk score
      │               ├─ score ≥ 0.65 → CRISIS OVERRIDE (no LLM)
      │               └─ ELSE → continue to LLM
      │
      ├─► Multimodal Fusion Engine
      │       ├─ text_distress × 0.65
      │       └─ face_distress × 0.35 → final_risk_score
      │
      └─► LLaMA 3 via Ollama (local, structured JSON)
              └─► PsychReport (Pydantic validated)

Webcam → Keras CNN → face emotion score → Fusion Engine
```

**Talking Points:**
- Walk through the flow top-to-bottom
- Emphasize: "The crisis engine runs BEFORE the LLM — if it triggers, the LLM is never called"
- Explain the fusion formula: `(Text × 0.65) + (Face × 0.35) = Final Risk Score`
- Highlight Pydantic validation: every output is Schema-enforced, never free-form text

---

## SLIDE 5 — The AI Models

**Title:** *Four AI Engines Working Together*

| # | Engine | Model | Purpose |
|---|--------|-------|---------|
| 1 | **Text Emotion** | DistilBERT (`bhadresh-savani/distilbert-base-uncased-emotion`) | Multi-label emotion classification from user text |
| 2 | **Crisis Detection** | MiniLM Zero-Shot NLI (`cross-encoder/nli-MiniLM2-L6-H768`) | Detects suicidal ideation, self-harm across 5 risk dimensions |
| 3 | **Face Emotion** | Custom Keras CNN + OpenCV Haar Cascade | 7-class real-time facial emotion detection via webcam |
| 4 | **Clinical Reasoning** | LLaMA 3 via Ollama (fully local) | Generates structured PsychReport with clinical-grade reasoning |

**Talking Points:**
- DistilBERT: lightweight transformer, 6 emotion classes — sadness, joy, fear, anger, surprise, love
- MiniLM NLI: this is NOT keyword matching — it uses natural language inference to understand MEANING
- Keras CNN: trained on FER2013 dataset, 7 classes (happy, sad, angry, fear, disgust, surprise, neutral)
- LLaMA 3: runs entirely locally via Ollama — zero data leaves the machine

---

## SLIDE 6 — PsychReport Output

**Title:** *Structured Clinical Output — The PsychReport*

**Display a sample JSON:**
```json
{
  "risk_classification": "MODERATE",
  "emotional_state_summary": "Elevated anxiety with undertones of helplessness.",
  "behavioral_inference": "User shows avoidance patterns and withdrawal.",
  "cognitive_distortions": ["Catastrophizing", "Mind Reading"],
  "suggested_interventions": [
    "Practice grounding exercises (5-4-3-2-1 technique)",
    "Schedule a session with a licensed therapist"
  ],
  "confidence_score": 0.78,
  "crisis_triggered": false
}
```

**Talking Points:**
- Every response is structured — not free-form chatbot text
- Risk levels: MINIMAL → LOW → MODERATE → HIGH → CRITICAL
- Cognitive distortions are CBT-based labels (catastrophizing, black-and-white thinking, etc.)
- The confidence score is the LLM's own self-assessed reliability metric
- If `crisis_triggered = true`, the report includes emergency resources automatically

---

## SLIDE 7 — Crisis Detection Deep-Dive

**Title:** *The Safety Net — Zero-Shot Crisis Detection*

**Key Points:**
- Uses **Natural Language Inference (NLI)** — not keyword matching
- Evaluates across 5 weighted risk dimensions:

| Risk Dimension | Weight |
|---------------|--------|
| Suicidal ideation | 1.00 |
| Self-harm intent | 1.00 |
| Immediate danger to self | 0.95 |
| Severe mental breakdown | 0.60 |
| Hopelessness and worthlessness | 0.50 |

- Threshold: `≥ 0.65` → **CRISIS OVERRIDE** → LLM is bypassed entirely
- Emergency resources (iCall, Vandrevala, AASRA) served automatically

**Talking Points:**
- "The phrase *'I don't see a future for myself'* would NOT be caught by keyword matching. Our NLI model understands its meaning."
- This layer runs BEFORE the LLM — it's the safety net of the entire system
- The response is deterministic — not generated by AI — to ensure reliability in critical moments

---

## SLIDE 8 — Tech Stack

**Title:** *Technology Stack*

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, TypeScript, TailwindCSS |
| **Backend** | Python 3.10, FastAPI, Uvicorn, Pydantic v2 |
| **LLM** | LLaMA 3 via Ollama (fully local, no API keys) |
| **Text Emotion** | HuggingFace Transformers — DistilBERT |
| **Crisis NLI** | HuggingFace Transformers — MiniLM Zero-Shot |
| **Face Emotion** | OpenCV + Custom Keras/TensorFlow CNN |
| **Database** | Supabase (PostgreSQL + Auth + RLS) |
| **Knowledge Base** | Pandas + CSV (Bhagavad Gita remedies) |
| **Deployment** | Docker Compose, Vercel (frontend) |
| **API Docs** | Swagger UI (auto-generated) |

**Talking Points:**
- Everything runs locally — no OpenAI, no Google API, no cloud LLM
- Supabase provides user authentication + row-level security — each user can only see their own data
- Docker Compose for one-command deployment of the entire stack

---

## SLIDE 9 — Live Demo (if applicable)

**Title:** *Live Demonstration*

**Demo Flow:**
1. Open the app → show the landing page
2. Type a message expressing mild anxiety → show the PsychReport panel
3. Toggle webcam → show real-time facial emotion in the sidebar
4. Type a high-risk message → show the crisis override in action
5. Navigate to history → show conversation storage with Supabase

**Tips:**
- Have Ollama running beforehand (`ollama serve` in a terminal)
- Have the backend and frontend already started
- Pre-test the crisis trigger with: *"I don't want to be here anymore, nothing matters"*

---

## SLIDE 10 — Future Roadmap

**Title:** *What's Next*

| Phase | Feature |
|-------|---------|
| v2.1 | Speech emotion analysis (audio modality) |
| v2.2 | TAT (Thematic Apperception Test) narrative analysis engine |
| v2.3 | Session-over-session longitudinal tracking |
| v3.0 | NeuroLink integration — EEG/EMG neural signal decoding |
| v3.x | Multi-language support (Hindi, Tamil, Bengali) |
| v4.0 | Institutional deployment (universities, corporate wellness programs) |

**Talking Points:**
- The fusion engine already has a `speech_score` placeholder — designed for expansion
- TAT analysis is already built separately and can be integrated
- NeuroLink is a sister project for neural-signal-based communication

---

## SLIDE 11 — Thank You + Q&A

**Content:**
- "Thank you" with team/contact info
- GitHub repo link
- Live demo URL: `psypredict.vercel.app`
- Disclaimer: *"PsyPredict is a clinical decision-support tool for educational purposes. It does not replace professional therapy."*

---
---

# 🚀 PART 2 — WORKFLOW, TECHNICAL DEEP-DIVE & BUSINESS PITCH

> Use this section for **viva voce, investor pitches, hackathon judging, or detailed technical Q&A**.

---

## 📐 I. System Workflow — Step by Step

### Complete Request Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER INTERACTION                          │
│  [Types message] + [Webcam captures face]                       │
└──────────────┬──────────────────────────────────┬───────────────┘
               │                                  │
               ▼                                  ▼
┌──────────────────────────┐         ┌────────────────────────────┐
│   DistilBERT Classifier  │         │  Keras CNN Face Detector   │
│   - 6 emotion labels     │         │  - Haar Cascade → face     │
│   - multi-label scores   │         │  - CNN → 7 emotion classes │
│   - dominant emotion     │         │  - confidence score        │
└──────────┬───────────────┘         └──────────┬─────────────────┘
           │                                    │
           ▼                                    │
┌──────────────────────────┐                    │
│   Crisis Engine (NLI)    │                    │
│   - 5 risk dimensions    │                    │
│   - weighted scoring     │                    │
│   - threshold = 0.65     │                    │
└──────────┬───────────────┘                    │
           │                                    │
     ┌─────┴──────┐                             │
     │ TRIGGERED? │                             │
     └─────┬──────┘                             │
      YES  │  NO                                │
      │    │                                    │
      │    ▼                                    │
      │  ┌─────────────────────────┐            │
      │  │  Multimodal Fusion      │◄───────────┘
      │  │  text × 0.65            │
      │  │  face × 0.35            │
      │  │  → final_risk_score     │
      │  └──────────┬──────────────┘
      │             │
      │             ▼
      │  ┌──────────────────────────┐
      │  │  LLaMA 3 (Ollama)       │
      │  │  - System prompt         │
      │  │  - Emotion context       │
      │  │  - Conversation history  │
      │  │  → Structured JSON       │
      │  └──────────┬───────────────┘
      │             │
      │             ▼
      │  ┌──────────────────────────┐
      │  │  Pydantic Validation     │
      │  │  → PsychReport schema    │
      │  └──────────┬───────────────┘
      │             │
      ▼             ▼
┌───────────────────────────────────┐
│         RESPONSE TO USER          │
│  - Conversational reply text      │
│  - PsychReport (structured)      │
│  - Text emotions breakdown       │
│  - Fusion risk score              │
│  - Remedy (if applicable)         │
│  - Crisis resources (if triggered)│
└───────────────────────────────────┘
```

### Key Workflow Principles
1. **Crisis-First Architecture** — Safety layer evaluates BEFORE the LLM is invoked
2. **Multimodal Fusion** — Never relies on a single source; combines text + visual signals
3. **Schema-Enforced Outputs** — Pydantic validation rejects malformed LLM responses
4. **Graceful Degradation** — If Ollama is down, a fallback report is returned with `service_degraded: true`
5. **Context Windowing** — Only last 10 conversation turns are sent to the LLM to prevent token overflow

---

## 🏗️ II. Architecture Types & Patterns

### Architecture Classification

| Dimension | Classification |
|-----------|---------------|
| **Overall** | Modular Monolith (backend) + SPA (frontend) |
| **API Pattern** | RESTful JSON API (FastAPI + auto-docs) |
| **AI Pattern** | Pipeline Architecture (sequential engine chain) |
| **Data Pattern** | Event-driven per-request (no batch processing) |
| **Auth Pattern** | Supabase Auth + Row-Level Security (RLS) |
| **Deployment** | Containerized (Docker Compose) |

### Design Patterns Used

| Pattern | Where It's Used |
|---------|----------------|
| **Singleton** | `crisis_engine`, `fusion_engine`, `text_emotion_engine` |
| **Strategy** | Emotion-to-distress score mapping (configurable) |
| **Pipeline** | Sequential engine chain: Text → Crisis → Fusion → LLM → Validation |
| **Fallback/Circuit Breaker** | Ollama retry with exponential backoff + fallback report |
| **Dependency Injection** | Settings loaded via `get_settings()` → engines read from config |
| **Schema Validation** | All I/O enforced through Pydantic models |

---

## 🧮 III. Models — Detailed Breakdown

### Model 1: DistilBERT Text Emotion Classifier
| Attribute | Detail |
|-----------|--------|
| **Model** | `bhadresh-savani/distilbert-base-uncased-emotion` |
| **Type** | Transformer (distilled BERT) |
| **Task** | Multi-label text emotion classification |
| **Classes** | sadness, joy, fear, anger, surprise, love |
| **Input** | User text (max 512 tokens) |
| **Output** | List of `{label, score}` pairs |
| **Why This Model** | Lightweight (66M params), fast inference on CPU, well-validated on emotion datasets |

### Model 2: MiniLM Zero-Shot NLI (Crisis Detection)
| Attribute | Detail |
|-----------|--------|
| **Model** | `cross-encoder/nli-MiniLM2-L6-H768` |
| **Type** | Cross-encoder Transformer (NLI) |
| **Task** | Zero-shot classification across 5 risk dimensions |
| **Input** | User text (max 512 chars) + candidate risk labels |
| **Output** | Per-label confidence scores → weighted sum → risk score |
| **Why This Model** | No fine-tuning needed; understands meaning, not just keywords; fast on CPU |

### Model 3: Custom Keras CNN (Facial Emotion)
| Attribute | Detail |
|-----------|--------|
| **Model** | Custom CNN trained on FER2013 |
| **Type** | Convolutional Neural Network |
| **Task** | 7-class facial emotion classification |
| **Classes** | happy, sad, angry, fear, disgust, surprise, neutral |
| **Input** | 48×48 grayscale face crop (via Haar Cascade) |
| **Output** | Predicted class + confidence score |
| **Why This Model** | Lightweight, runs in real-time on webcam feed, no GPU required |

### Model 4: LLaMA 3 (Clinical Reasoning)
| Attribute | Detail |
|-----------|--------|
| **Model** | LLaMA 3 8B via Ollama |
| **Type** | Large Language Model (decoder-only Transformer) |
| **Task** | Structured clinical reasoning → PsychReport JSON |
| **Input** | System prompt + emotion context + conversation history |
| **Output** | JSON conforming to PsychReport schema |
| **Why This Model** | Fully local (no API keys), strong instruction-following, JSON-mode support |

### Fusion Formula
```
text_distress = map(dominant_text_emotion → distress_score)
face_distress = map(face_emotion → distress_score)

final_risk_score = (TEXT_WEIGHT × text_distress) + (FACE_WEIGHT × face_distress)
                 = (0.65 × text_distress) + (0.35 × face_distress)
```

Distress score mappings:
- **Text:** sadness=0.85, fear=0.80, anger=0.60, disgust=0.50, surprise=0.30, joy=0.05
- **Face:** fear=0.80, sad=0.70, angry=0.50, disgust=0.40, surprised=0.30, neutral=0.20, happy=0.05

---

## 💼 IV. Business Pitch

### 🎯 The Problem (Market Gap)

- **970 million** people worldwide suffer from mental disorders (WHO)
- India: **150 million+** people need mental health support; **< 9,000** psychiatrists available
- Existing apps are glorified chatbots — no clinical depth, no multimodal analysis, no real crisis detection
- Most solutions require cloud APIs → **privacy nightmare** for sensitive mental health data

### 💡 Our Solution

PsyPredict is the **first fully-local, multimodal, clinical-grade mental health AI system** that:
1. Combines **4 AI models** for accurate emotional understanding
2. Produces **structured clinical reports**, not chatbot replies
3. Runs **100% locally** — zero data leaves the user's machine
4. Has a **deterministic crisis safety net** that cannot be fooled by paraphrasing

### 🧑‍🤝‍🧑 Target Users

| Segment | Use Case |
|---------|----------|
| **University Counseling Centers** | Triage incoming students, prioritize high-risk cases |
| **Corporate Wellness Programs** | Anonymous employee mental health screening |
| **Telehealth Platforms** | Pre-session assessment before therapist consultation |
| **Clinical Psychologists** | Decision-support tool during sessions |
| **Individual Users** | Self-awareness and emotional tracking |
| **NGOs & Government Programs** | Scalable mental health screening in underserved areas |
| **Schools (K-12)** | Early detection of at-risk students |

### ⭐ Unique Selling Points (USPs)

| # | USP | Why It Matters |
|---|-----|---------------|
| 1 | **Fully Local AI** | No cloud, no data leaks — HIPAA/DISHA compliant by design |
| 2 | **Multimodal Fusion** | Text + Face = more accurate than single-modality systems |
| 3 | **Structured Clinical Output** | Every response is a validated `PsychReport`, not free-form text |
| 4 | **NLI-Based Crisis Detection** | Understands meaning, not keywords — catches subtle distress |
| 5 | **LLM Override Safety Net** | Crisis layer is deterministic — AI cannot hallucinate in emergencies |
| 6 | **Culturally Grounded** | Bhagavad Gita remedies for Indian user base |
| 7 | **Open Source** | MIT License — inspectable, auditable, trustworthy |
| 8 | **Zero API Cost** | No OpenAI/Google bills — runs on commodity hardware |

### 📈 Scalability & Expansion Plan

```
PHASE 1 (Current)          PHASE 2 (6 months)           PHASE 3 (12 months)
─────────────────          ──────────────────           ───────────────────
• Text + Face              • + Speech Emotion           • + EEG/EMG (NeuroLink)
• LLaMA 3 local            • + TAT Narrative Analysis   • + Multi-language (Hindi, Tamil)
• Single user              • Multi-user (Supabase Auth)  • Institutional dashboards
• Docker local             • Cloud deploy (GPU VMs)      • White-label SaaS
• English only             • Session analytics           • Therapist-in-the-loop mode
```

**Scaling Strategy:**
1. **Horizontal:** Deploy on cloud VMs with GPU for institutional use
2. **Vertical:** Add more modalities (speech, neural signals)
3. **Geographic:** Multi-language support for Indian regional languages
4. **Market:** White-label SaaS for hospitals, universities, corporates
5. **Data:** Longitudinal tracking for treatment efficacy measurement

### 💰 Revenue Model (Potential)

| Stream | Description |
|--------|------------|
| **Freemium** | Free for individuals, paid for advanced analytics |
| **Institutional License** | Annual SaaS license for universities/hospitals |
| **API-as-a-Service** | Sell the PsychReport pipeline to other mental health apps |
| **White-Label** | Custom-branded deployments for corporate clients |
| **Research Grants** | Collaborate with psychology departments for funded studies |

### 🏆 Credibility & Validation

| Factor | Evidence |
|--------|---------|
| **Clinical Framework** | Based on CBT (Cognitive Behavioral Therapy) distortion detection |
| **Validated Models** | DistilBERT trained on GoEmotions; FER2013 for facial emotion |
| **Safety Engineering** | Zero-shot NLI crisis detection with deterministic overrides |
| **Production Quality** | Input sanitization, rate limiting, exponential backoff, structured logging |
| **Data Privacy** | Fully local inference; Supabase RLS for user data isolation |
| **Open Source** | MIT License — full code transparency and auditability |
| **Disclaimer** | Clearly stated: decision-support tool, not a replacement for therapy |

---

## 🛡️ V. Technical Stack — Complete Reference

### Backend Stack
| Component | Technology | Version / Detail |
|-----------|-----------|-----------------|
| Language | Python | 3.10 |
| Framework | FastAPI | Async, auto-docs |
| Server | Uvicorn | ASGI server |
| Validation | Pydantic v2 | All I/O schemas |
| ML - Text | HuggingFace Transformers | DistilBERT, MiniLM |
| ML - Vision | TensorFlow/Keras, OpenCV | CNN + Haar Cascade |
| LLM | Ollama | LLaMA 3 (local) |
| Data | Pandas | CSV knowledge base |

### Frontend Stack
| Component | Technology | Version / Detail |
|-----------|-----------|-----------------|
| Language | TypeScript | Strict mode |
| Framework | React | 18.x |
| Build Tool | Vite | Fast HMR |
| Styling | TailwindCSS | Utility-first |
| HTTP Client | Axios | Typed API calls |
| Routing | React Router | SPA navigation |
| State | React Context | Auth + chat state |
| Webcam | HTML5 MediaDevices API | Live feed |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth + RLS |
| Containerization | Docker + Docker Compose |
| Frontend Hosting | Vercel |
| Backend Hosting | Any VM with Ollama (GPU recommended) |
| API Documentation | Swagger UI (auto-generated at `/docs`) |

### Database Schema (Supabase)
```
conversations (id, user_id, created_at, title)
     │
     └── messages (id, user_id, conversation_id, content, metadata, created_at)

profiles (id, updated_at, full_name, avatar_url, email, password_hash)
```
- Row-Level Security (RLS) enabled on all tables
- Users can only read/write their own data
- Profiles decoupled from `auth.users` to prevent race conditions

---

## 🎙️ VI. Common Viva / Q&A Questions & Answers

### Q1: "Why not just use ChatGPT?"
> ChatGPT is a cloud-based general chatbot. PsyPredict is a **local, multimodal clinical AI** that combines 4 specialized models, produces structured clinical reports, and has a deterministic crisis safety net. ChatGPT sends all data to OpenAI's servers — PsyPredict keeps everything on your machine.

### Q2: "How is your crisis detection better than keyword matching?"
> We use Natural Language Inference (NLI) via MiniLM. The sentence *"I don't see any reason to continue"* has zero crisis keywords but our model scores it as high-risk because it *understands the meaning*. Keyword matchers would miss it entirely.

### Q3: "What if the LLM hallucinates?"
> Every LLM output is validated against a Pydantic schema (`PsychReport`). If the output doesn't conform, it's rejected. For critical cases, the crisis layer bypasses the LLM entirely — the response is deterministic and pre-written.

### Q4: "Can this replace a therapist?"
> No, and it's not designed to. PsyPredict is a **clinical decision-support tool** — it helps triage, screen, and support. It explicitly directs high-risk users to professional help. Our disclaimer makes this clear.

### Q5: "Why run locally instead of using cloud APIs?"
> Mental health data is among the most sensitive personal data. Sending it to third-party APIs creates privacy, compliance, and cost risks. Local inference via Ollama means **zero data exposure** and **zero API costs**.

### Q6: "What is multimodal fusion and why does it matter?"
> A person might type "I'm fine" while their face shows fear. Single-modality analysis would miss this. Our fusion engine combines text emotion (65% weight) and facial emotion (35% weight) to produce a more accurate risk score.

### Q7: "How accurate is the system?"
> DistilBERT achieves ~93% accuracy on the GoEmotions benchmark. The Keras CNN achieves ~65% on FER2013 (standard for the field). The fusion of multiple modalities compensates for individual model weaknesses.

### Q8: "What makes this production-ready?"
> Input sanitization (HTML stripping, char limits), rate limiting (30 req/min), exponential backoff on Ollama failures, graceful fallbacks, structured logging, Pydantic validation on all I/O, context window trimming, and Docker deployment.

---

## 🗂️ VII. API Reference (Quick)

| Method | Endpoint | What It Does |
|--------|----------|-------------|
| `POST` | `/api/chat` | Full clinical pipeline → PsychReport + conversational reply |
| `POST` | `/api/predict/emotion` | Facial emotion detection from webcam frame |
| `POST` | `/api/analyze/text` | Text emotion analysis + crisis pre-screen |
| `GET` | `/api/get_advice?condition=` | Bhagavad Gita remedy lookup |
| `GET` | `/api/health` | System health check (Ollama + DistilBERT status) |

---

## 📋 VIII. Presentation Checklist

### Before the Presentation
- [ ] Ollama is installed and running (`ollama serve`)
- [ ] LLaMA 3 model is pulled (`ollama list` shows `llama3`)
- [ ] Backend is running (`uvicorn app.main:app --host 0.0.0.0 --port 7860`)
- [ ] Frontend is running (`npm run dev` → `localhost:5173`)
- [ ] Webcam is working and browser has camera permission
- [ ] Swagger UI is accessible at `localhost:7860/docs`
- [ ] Test crisis trigger with a sample message beforehand

### Presentation Tips
1. **Start with the problem** — make the audience feel the gap before showing the solution
2. **Show, don't tell** — live demo > slides for technical features
3. **Emphasize the safety net** — crisis detection is the most impressive differentiator
4. **Use the PsychReport** — show the JSON output to demonstrate clinical depth
5. **Privacy angle** — "Everything runs locally" is a powerful statement
6. **Cultural touch** — the Bhagavad Gita remedies show thoughtfulness beyond just tech
7. **End with scale** — show the roadmap to demonstrate vision beyond the current version
8. **Keep it under 12 minutes** — leave time for Q&A
9. **Have backup screenshots** — in case the live demo fails

---

> *"PsyPredict doesn't just ask how you're feeling — it actually understands."*

---

*Guide prepared by PsyPredict Team — March 2026*
