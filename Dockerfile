# This Dockerfile is provided for reference only.
# For manual deployment on Ubuntu, please follow the instructions in README.md

FROM python:3.12-slim as builder

# Build stage - install dependencies
WORKDIR /build
COPY requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser appuser \
    && mkdir -p /home/appuser/.local \
    && chown -R appuser:appuser /home/appuser

# Copy Python packages from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Create directories for data, cache, and logs
RUN mkdir -p /app/data/posters /app/cache /app/logs \
    && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser epg_collector/ ./epg_collector/
COPY --chown=appuser:appuser .env.example ./.env.example

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "epg_collector.api.app:app", "--host", "0.0.0.0", "--port", "8000"]