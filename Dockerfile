# syntax=docker/dockerfile:1
FROM python:3.12-slim as builder

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Продакшен образ
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH=/home/appuser/.local/bin:$PATH

# Создаем пользователя без прав root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости Python
COPY --from=builder /root/.local /home/appuser/.local

WORKDIR /app

# Копируем код приложения
COPY . .

# Создаем необходимые директории и устанавливаем права
RUN mkdir -p data logs cache && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "epg_collector.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
