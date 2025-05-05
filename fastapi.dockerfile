# filepath: /home/liron/Phonexa/fastapi.dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including phonemizer requirements
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 espeak-ng libespeak-ng-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for HuggingFace cache
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV HF_HOME=/app/model_cache

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]