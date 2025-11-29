# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /app

# No need to specify a directory path since context is already LLMTeacher
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]