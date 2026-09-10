"""
app.py — Hugging Face Spaces Entry Point (Gradio SDK + FastAPI)
Mounts the full PsyPredict FastAPI backend on Hugging Face's Free CPU Basic (16 GB RAM).
"""
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

import gradio as gr
from app.main import app as fastapi_app

# Satisfy ZeroGPU hardware requirement on Hugging Face Spaces
try:
    import spaces

    @spaces.GPU(duration=60)
    def _zero_gpu_init():
        """Satisfies ZeroGPU startup check on Hugging Face"""
        return True

    _zero_gpu_init()
except Exception:
    pass


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
        - 🌐 **Frontend**: Hosted on [Vercel](https://psy-predict-v3.vercel.app)
        """
    )

# Mount Gradio onto the existing FastAPI app
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

