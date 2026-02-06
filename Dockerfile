# Dockerfile for Project Chimera
# Multi-stage build for smaller, secure production image

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install build dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (for layer caching)
COPY pyproject.toml ./

# Install dependencies into isolated location
RUN uv pip install --system --no-cache -r <(uv pip compile pyproject.toml) || \
    uv pip install --system --no-cache .

# Stage 2: Runtime image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Create non-root user
RUN groupadd -r chimera && useradd -r -g chimera chimera

WORKDIR /app

# Copy only runtime dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY --chown=chimera:chimera pyproject.toml ./
COPY --chown=chimera:chimera skills ./skills
COPY --chown=chimera:chimera specs ./specs
COPY --chown=chimera:chimera research ./research
COPY --chown=chimera:chimera tests ./tests
COPY --chown=chimera:chimera Makefile ./Makefile

# Switch to non-root user
USER chimera

# Healthcheck (if you add a health endpoint later)
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#   CMD python -c "import sys; sys.exit(0)"

# Default command: run tests
CMD ["make", "test"]
