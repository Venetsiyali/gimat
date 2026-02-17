# Ultra-minimal Dockerfile - guaranteed to work
FROM python:3.10-slim

WORKDIR /app

# Install ONLY FastAPI and uvicorn
RUN pip install --no-cache-dir fastapi==0.109.0 uvicorn==0.27.0

# Copy ONLY main.py
COPY main.py .

# Expose port
EXPOSE 8000

# Simple CMD
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
