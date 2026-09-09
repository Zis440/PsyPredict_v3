"""
app.py — Hugging Face Spaces Entry Point (Gradio SDK + FastAPI)
Mounts the full PsyPredict FastAPI backend on Hugging Face's Free CPU Basic (16 GB RAM).
"""
import os
import sys

# Ensure ML models and datasets are downloaded if not already present in the Space
try:
    import download_models
    print("🚀 Initializing PsyPredict ML Model Assets...")
    download_models.download_drive_file(download_models.MODEL_ID, download_models.FACE_MODEL_PATH)
    download_models.download_drive_file(download_models.CSV_ID, download_models.MEDS_CSV_PATH)
    download_models.download_hf_directory(download_models.CRISIS_MODEL_REPO, download_models.CRISIS_MODEL_PATH)
    download_models.download_hf_directory(download_models.DISTILBERT_MODEL_REPO, download_models.DISTILBERT_MODEL_PATH)
    print("✅ All ML Model Assets Ready.")
except Exception as e:
    print(f"⚠️ Model download warning: {e}")

import gradio as gr
from app.main import app as fastapi_app

# Minimal UI displayed when directly viewing the Hugging Face Space URL in browser
with gr.Blocks(title="PsyPredict Backend API") as demo:
    gr.Markdown("# 🧠 PsyPredict — Clinical Multimodal AI Backend")
    gr.Markdown(
        """
        ### 🟢 Backend Status: **ONLINE**
        This Space powers the **PsyPredict API** with 16 GB RAM (DistilBERT + MiniLM + Keras + Groq Llama 3.3).
        
        - 🔗 **API Health**: [`/api/health`](./api/health)
        - 📖 **Interactive API Docs (Swagger)**: [`/docs`](./docs)
        - 💬 **Therapist Endpoint**: `POST /api/chat`
        - 🌐 **Frontend**: Hosted on [Vercel](https://vercel.com)
        """
    )

# Mount Gradio onto the existing FastAPI app at root
# All existing FastAPI routes (/api/*, /docs, CORS) remain fully functional
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
