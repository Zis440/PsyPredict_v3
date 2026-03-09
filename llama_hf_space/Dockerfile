# Use standard Python image (Debian based, not Alpine/Musl)
FROM python:3.10

WORKDIR /app

# Install system dependencies needed for llama-cpp-python
RUN apt-get update && apt-get install -y --fix-missing --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Install llama-cpp-python from pre-built CPU wheels (avoids 30+ min compile time)
RUN pip install --no-cache-dir --prefer-binary \
    llama-cpp-python==0.3.2 \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

COPY . .

# Hugging Face Space default port
EXPOSE 7860

# Run the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
