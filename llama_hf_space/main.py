import os
import urllib.request
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="Llama 3 Dedicated API")

# Llama 3 8B Instruct GGUF
# Note: If 16GB free tier still crashes, change this to the Q2_K_M version.
MODEL_URL = "https://huggingface.co/MaziyarPanahi/Llama-3-8B-Instruct-v0.1-GGUF/resolve/main/Llama-3-8B-Instruct-v0.1.Q4_K_M.gguf"
MODEL_PATH = "model.gguf"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("⬇️ Downloading model (this may take a few minutes)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("✅ Model downloaded.")

download_model()

# Initialize Llama (loads it into memory)
print("🚀 Loading model into memory...")
from llama_cpp import Llama
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=os.cpu_count() or 4,
    verbose=False
)
print("✅ Model ready.")

class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: Optional[bool] = False
    options: Optional[Dict[str, Any]] = {}

@app.post("/api/generate")
async def generate(req: GenerateRequest):
    """
    Mimics the Ollama /api/generate endpoint so your existing
    PsyPredict code (ollama_engine.py) doesn't need to change!
    """
    temperature = req.options.get("temperature", 0.2) if req.options else 0.2
    top_p = req.options.get("top_p", 0.9) if req.options else 0.9
    
    if req.stream:
        def stream_generator():
            stream = llm(
                prompt=req.prompt,
                max_tokens=600,
                temperature=temperature,
                top_p=top_p,
                stream=True,
                stop=["USER:", "CURRENT USER INPUT:"]
            )
            for chunk in stream:
                token = chunk["choices"][0]["text"]
                yield json.dumps({"response": token, "done": False}) + "\n"
            yield json.dumps({"response": "", "done": True}) + "\n"
            
        return StreamingResponse(stream_generator(), media_type="application/x-ndjson")
    else:
        response = llm(
            prompt=req.prompt,
            max_tokens=600,
            temperature=temperature,
            top_p=top_p,
            stop=["USER:", "CURRENT USER INPUT:"]
        )
        return {"response": response["choices"][0]["text"]}

@app.get("/api/tags")
def tags():
    """Health check used by PsyPredict's ollama_engine.py"""
    return {"models": [{"name": "llama3"}]}

@app.get("/")
def home():
    return {"status": "Llama 3 API is running!"}
