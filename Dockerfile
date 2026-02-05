# Dockerfile for Project Chimera
# Uses the Python environment defined in pyproject.toml and runs tests via `make`.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (can be extended later if Postgres/Weaviate/Redis clients need extras)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv for managing dependencies from pyproject.toml
RUN pip install --no-cache-dir uv

# Copy project metadata and tests
COPY pyproject.toml ./pyproject.toml
COPY skills ./skills
COPY specs ./specs
COPY research ./research
COPY tests ./tests

# Install Python dependencies based on pyproject.toml
# Using `--system` so they install into the base environment.
RUN uv pip install --system .

# Default command: run tests via make (Makefile is copied separately)
COPY Makefile ./Makefile

CMD ["make", "test"]

