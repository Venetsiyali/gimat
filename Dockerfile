# ======================================
# Ultra-lightweight Railway Dockerfile
# Target size: <1GB (Railway limit: 4GB)
# ======================================

FROM python:3.10-slim as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install minimal build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ======================================
# Final ultra-slim image
# ======================================
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install ONLY runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/*

# Copy ONLY installed packages (not build tools)
COPY --from=builder /root/.local /root/.local

# Create minimal app structure
WORKDIR /app

# Copy ONLY necessary Python files
COPY --chown=nobody:nogroup backend/main.py backend/
COPY --chown=nobody:nogroup backend/api backend/api/
COPY --chown=nobody:nogroup backend/database backend/database/
COPY --chown=nobody:nogroup backend/models backend/models/
COPY --chown=nobody:nogroup backend/rag backend/rag/

# Non-root user
USER nobody

EXPOSE 8000

# Simple health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:8000/health || exit 1

# Start with minimal resources
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
