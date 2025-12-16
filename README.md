# 🌿 **PsyPredict**
> *AI-Augmented Multi-Modal Mental Health Assistance System*

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Status](https://img.shields.io/badge/status-active-success.svg) ![Python](https://img.shields.io/badge/backend-python-yellow.svg) ![React](https://img.shields.io/badge/frontend-react-cyan.svg) ![Vercel](https://img.shields.io/badge/frontend-Vercel-black) ![HuggingFace](https://img.shields.io/badge/backend-Hugging%20Face-yellow)


---

## **📖 Overview**

**PsyPredict** is an advanced mental-health assistance system designed to understand a user’s emotional state through **facial expression analysis** and **text interpretation**. 

Unlike standard chatbots, PsyPredict combines computer vision with a therapeutic LLM engine to provide accessible, culturally meaningful, and personalized support. It integrates modern AI techniques with traditional wisdom, offering guidance inspired by the **Bhagavad Gita**.

---

## ✨ **Key Features**

### **1. Multi-Modal Emotion Understanding**
* **Facial Analysis:** Detects live emotions (sadness, anger, fear, stress, confusion) using Computer Vision.
* **Text Analysis:** Interprets emotional tone, symptoms, and behavioral patterns from user text.
* **Fusion Logic:** Combines visual and textual data for a highly accurate emotional profile.

### **2. Therapeutic AI Engine**
* **Powered by Google Gemini 2.0 Flash:** A fast, empathetic reasoning engine that acts as a compassionate companion.
* **Context Aware:** Remembers session history and tracks emotional trends over time.
* **Safety First:** Detects crisis keywords and routes to emergency resources when necessary.

### **3. Bhagavad Gita–Based Remedy System**
* Translates ancient shlokas into simple, story-based psychological guidance.
* Provides culturally grounded advice that feels human and comforting, not robotic.

### **4. Interactive Dashboard**
* Real-time emotion tracking graph.
* Personalized non-prescriptive lifestyle recommendations.

---

## 🧩 **System Architecture**

```mermaid
graph TD;
    A[User] -->|Webcam Video| B(Facial Emotion Model);
    A -->|Chat Text| C(Text Analysis);
    B --> D{Fusion Engine};
    C --> D;
    D -->|Context + Emotion| E[LLM Therapist];
    E -->|Personalized Response| A;
````

*(Or using the text-based version below)*

```
PsyPredict
│
├── Facial Emotion Module (CV)
│     ├── Live video capture
│     └── Emotion classification (CNN)
│
├── Therapist Engine (LLM)
│     ├── Powered by Gemini 2.0 Flash
│     ├── Bhagavad Gita Knowledge Base
│     └── Context Management
│
└── Frontend Interface
      ├── React + Vite
      └── Real-time Visualization
```

-----

## 🛠️ **Tech Stack**

| Component | Technology |
| :--- | :--- |
| **Frontend** | React, Vite, TypeScript, TailwindCSS |
| **Backend** | Python (Flask/FastAPI) |
| **AI / LLM** | **Google Gemini 2.0 Flash**, LangChain |
| **CV Model** | OpenCV, DeepFace / Custom CNN |

-----

## 📂 **Folder Structure**

```bash
PsyPredict/
├── backend/
│   ├── llm_engine.py    # Gemini 2.0 Integration
│   ├── app.py           # API Entry point
│   ├── models/          # Emotion detection models
│   └── .env             # API Keys (Google AI Studio)
├── frontend/
│   ├── src/
│   │   ├── components/  # Chat & Camera UI
│   │   └── hooks/       # Custom React Hooks
│   └── package.json
└── README.md
```

-----

## 🚀 **Getting Started**

### **1. Clone the Repository**

```bash
git clone https://github.com/therandomuser03/psypredict.git
cd psypredict
```

### **2. Backend Setup**

Navigate to the backend folder and install dependencies:

```bash
cd backend
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Setup Environment Variables
# Create a .env file and add: GOOGLE_API_KEY=your_key_here
```

Run the server:

```bash
python app.py
```

### **3. Frontend Setup**

Open a new terminal for the frontend:

```bash
cd frontend
npm install
npm run dev
```

Access the app at `http://localhost:5173`.

-----

## 🌍 **Deployment**

The project is deployed using a modern cloud-based setup:

- **Frontend:** Deployed on **Vercel**  
  👉 https://psypredict.vercel.app

- **Backend:** Deployed on **Hugging Face Spaces**  
  👉 https://huggingface.co/spaces/therandomuser03/psypredict-backend

This separation ensures fast global delivery of the UI while leveraging Hugging Face’s optimized infrastructure for AI model inference.

-----

## ⚠️ **Disclaimer**

> **Important:** This system is intended for **emotional support and educational purposes only**. It does **not** provide medical diagnosis or professional therapy. If you or someone you know is in crisis, please contact emergency services or a licensed mental health professional immediately.

-----

## 🤝 **Contributing**

Contributions are welcome\! Please fork the repo and submit a pull request.

## 📄 **License**

This project is licensed under the **MIT License**.  
See the full license text here: **[LICENSE](./LICENSE)**.
