# syntax=docker/dockerfile:1

# Pinned to bookworm (Debian 12), not the floating "slim" tag: Playwright's
# `--with-deps` apt package list (ttf-unifont, ttf-ubuntu-font-family, etc.)
# doesn't resolve on Debian trixie (13), which "python:3.12-slim" now points
# to as of late-2025 image rebuilds.
FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only, to keep image smaller)
RUN playwright install --with-deps chromium

FROM base AS final

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY . .
RUN mkdir -p /app/storage/resumes /app/storage/screenshots \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
