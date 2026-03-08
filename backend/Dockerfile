# 1. Use Python 3.10 slim
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies
#    - libgl1/libglib2.0-0: OpenCV needs these
#    - build-essential/cmake: needed to compile llama-cpp-python from source
RUN apt-get update && apt-get install -y --fix-missing --no-install-recommends -o Acquire::Retries=3 \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 4. Install PyTorch CPU-only FIRST (saves ~1.5GB vs full CUDA torch)
#    This is a separate layer so it caches well
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

# 5. Install llama-cpp-python from pre-built CPU wheels (avoids 30+ min C++ compile)
#    PINNED to 0.3.2 — the latest version with pre-built wheels on the abetlen index.
#    Without the pin, pip resolves 0.3.16+ from PyPI which has NO pre-built wheel
#    and falls back to compiling llama.cpp from source (times out on HF Spaces).
RUN pip install --no-cache-dir --prefer-binary \
    llama-cpp-python==0.3.2 \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# 6. Install remaining Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy your code
COPY . .

# 8. Download all ML models (Face, Text, LLaMA 3 GGUF) during build
RUN python download_models.py

# 9. Environment & Port settings (7860 is HF Spaces standard)
ENV PYTHONPATH=/app
ENV USE_EMBEDDED_LLM=True
ENV HF_HUB_OFFLINE=1
EXPOSE 7860

# 10. Run the app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]