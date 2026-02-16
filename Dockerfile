# ======================================
# Optimized Production Dockerfile for GIMAT
# Railway.app deployment
# Python 3.10-slim base
# ======================================

FROM python:3.10-slim as base

# Metadata
LABEL maintainer="GIMAT Team"
LABEL description="Gidrologik Intellektual Monitoring va Axborot Tizimi"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# ======================================
# Dependencies stage (cached layer)
# ======================================
FROM base as dependencies

# Copy only requirements first (for better caching)
COPY backend/requirements.txt .

# Install Python dependencies
# Use --no-cache-dir to reduce image size
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ======================================
# Production stage
# ======================================
FROM base as production

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Create app user (security best practice)
RUN useradd -m -u 1000 gimat && \
    mkdir -p /app/logs /app/data /app/cache && \
    chown -R gimat:gimat /app

# Copy application code
COPY --chown=gimat:gimat backend/ /app/backend/

# Switch to non-root user
USER gimat

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
