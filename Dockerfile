# Railway-compatible Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install deps
RUN pip install --no-cache-dir fastapi==0.109.0 uvicorn==0.27.0

# Copy app
COPY main.py .

# Railway provides PORT env variable
ENV PORT=8000

# Dynamic port binding
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
