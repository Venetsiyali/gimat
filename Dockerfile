# ======================================
# Railway Dockerfile - NO HEALTHCHECK
# Let Railway handle health checks via HTTP
# ======================================

FROM python:3.10-slim as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ======================================
# Runtime
# ======================================
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Minimal runtime deps (NO curl/wget)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app
COPY backend/ backend/

EXPOSE $PORT

# NO HEALTHCHECK - Railway does it via HTTP
# Railway will check GET /health automatically

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
