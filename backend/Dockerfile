# 1. Use Python 3.10 slim
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install minimal system dependencies
#    - libgl1/libglib2.0-0: OpenCV needs these
#    - build-essential/python3-dev: llama-cpp-python builds from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Install PyTorch CPU-only FIRST (saves ~1.5GB vs full CUDA torch)
#    This is a separate layer so it caches well
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

# 5. Install remaining Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy your code
COPY . .

# 7. Download all ML models (Face, Text, LLaMA 3 GGUF) during build
RUN python download_models.py

# 8. Environment & Port settings (7860 is HF Spaces standard)
ENV PYTHONPATH=/app
ENV USE_EMBEDDED_LLM=True
EXPOSE 7860

# 9. Run the app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]