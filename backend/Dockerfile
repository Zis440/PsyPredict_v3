# 1. Use Python 3.10
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies (including build tools for llama-cpp-python if needed)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your code
COPY . .

# 6. Download all ML models (Face, Text, LLaMA 3 GGUF) during build
# This ensures a "batteries included" image for HF Spaces
RUN python download_models.py

# 7. Environment & Port settings (7860 is HF Spaces standard)
ENV PYTHONPATH=/app
ENV USE_EMBEDDED_LLM=True
EXPOSE 7860

# 8. Run the app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]