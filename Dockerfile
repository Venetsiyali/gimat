# ======================================
# Railway-optimized Dockerfile
# Fixed: Health check and PORT variable
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
# Runtime image
# ======================================
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# Copy backend files
COPY backend/ backend/

# Create empty __init__.py if missing
RUN touch backend/__init__.py && \
    touch backend/api/__init__.py && \
    touch backend/database/__init__.py

EXPOSE $PORT

# Simplified health check (use wget if curl fails)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT}/health || exit 1

# Start app (Railway provides $PORT)
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
