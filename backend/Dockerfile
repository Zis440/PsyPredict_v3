# 1. Use Python 3.10
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your code (and datasets) into the container
COPY . .

ENV PYTHONPATH=/app

# 6. Expose the port (5000 is standard for Flask)
EXPOSE 5000

# 7. Run the app
CMD ["python", "app/main.py"]