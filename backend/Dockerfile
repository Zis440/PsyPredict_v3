# Use Python 3.10 Slim (Smaller & Faster)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (Required for OpenCV/Computer Vision)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Expose port (Matches your Flask/FastAPI port)
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]