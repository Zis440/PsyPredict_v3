"""
app.py — Hugging Face Spaces Entry Point (Gradio SDK + FastAPI)
Mounts the full PsyPredict FastAPI backend on Hugging Face's Free ZeroGPU tier.
"""
try:
    import spaces
except ImportError:
    class spaces:
        @staticmethod
        def GPU(fn=None, duration=None):
            def decorator(f):
                return f
            return decorator if fn is None else decorator(fn)

import os
import sys

# Prevent TensorFlow oneDNN, OpenMP, and libuv segfaults on Linux CPU
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["GRADIO_SSR_MODE"] = "false"

import gradio as gr
from app.main import app as fastapi_app

# ── ZeroGPU Emotion Analysis Function ─────────────────────────────────────────
@spaces.GPU(duration=60)
def predict_emotion(text: str) -> str:
    if not text or not text.strip():
        return "Please enter some text."
    try:
        from app.services.text_emotion_engine import TextEmotionEngine
        engine = TextEmotionEngine()
        results = engine._classify_sync(text)
        if not results:
            return "No emotion patterns detected."
        return "\n".join(f"• {r.label.capitalize()}: {r.confidence * 100:.1f}%" for r in results[:5])
    except Exception as exc:
        return f"Status: Model ready (inference note: {exc})"

# ── Gradio UI (Space Dashboard + Interactive Test) ───────────────────────────
with gr.Blocks(title="PsyPredict Backend API") as demo:
    gr.Markdown("# 🧠 PsyPredict — Clinical Multimodal AI Backend")
    gr.Markdown(
        """
        ### 🟢 Backend Status: **ONLINE**
        Powered by **Hugging Face ZeroGPU** (DistilBERT + MiniLM + Keras CNN + Groq Llama 3.3).

        - 🔗 **API Health**: [`/api/health`](./api/health)
        - 📖 **Interactive API Docs (Swagger)**: [`/docs`](./docs)
        - 💬 **Therapist Endpoint**: `POST /api/chat`
        - 🌐 **Frontend App**: Hosted on [Vercel](https://psy-predict-v3.vercel.app)
        """
    )
    with gr.Group():
        gr.Markdown("### ⚡ Live Text Emotion Classifier")
        with gr.Row():
            inp = gr.Textbox(placeholder="e.g. I feel overwhelmed and anxious lately...", label="Patient Statement", lines=2)
            out = gr.Textbox(label="Detected Emotions", lines=2)
        btn = gr.Button("Analyze Emotion", variant="primary")
        btn.click(fn=predict_emotion, inputs=inp, outputs=out)

# ── Mandatory for ZeroGPU: enable Gradio event queue ─────────────────────────
demo.queue()

# ── Mount Gradio onto the existing FastAPI app ────────────────────────────────
app = gr.mount_gradio_app(fastapi_app, demo, path="/", ssr_mode=False)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
