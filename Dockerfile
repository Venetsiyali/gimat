# ======================================
# Optimized Railway Dockerfile
# Fast build (~2-3 minutes)
# ======================================

FROM python:3.10-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ======================================
# Dependencies stage
# ======================================
FROM base as dependencies

COPY backend/requirements.txt .

# Install with timeout optimization
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --timeout 1000 -r requirements.txt

# ======================================
# Production stage
# ======================================
FROM base as production

COPY --from=dependencies /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Create non-root user
RUN useradd -m -u 1000 gimat && \
    mkdir -p /app/logs /app/data && \
    chown -R gimat:gimat /app

COPY --chown=gimat:gimat backend/ /app/backend/

USER gimat

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Single worker for cost efficiency
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
