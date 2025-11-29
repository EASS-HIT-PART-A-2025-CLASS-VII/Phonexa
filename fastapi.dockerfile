# filepath: /home/liron/Phonexa/fastapi.dockerfile
# syntax=docker/dockerfile:1
# filepath: /home/liron/Phonexa/fastapi.dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including phonemizer requirements
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 espeak-ng libespeak-ng-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt

# Set environment variables for HuggingFace cache
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV HF_HOME=/app/model_cache

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]