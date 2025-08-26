#!/bin/bash

echo "========================================"
echo "  IPTV EPG Collector - Режим разработки"
echo "========================================"
echo

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "[ОШИБКА] Docker не установлен"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "[ОШИБКА] Docker Compose не установлен"
    exit 1
fi

echo "[INFO] Запускаем в режиме разработки..."
docker-compose -f docker-compose.dev.yml up -d

if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось запустить контейнеры"
    exit 1
fi

echo
echo "[SUCCESS] Режим разработки запущен!"
echo
echo "Frontend (Vite): http://localhost:5173"
echo "Backend API:     http://localhost:8000"
echo "API Docs:        http://localhost:8000/docs"
echo
echo "Для просмотра логов: docker-compose -f docker-compose.dev.yml logs -f"
echo "Для остановки: docker-compose -f docker-compose.dev.yml down"
echo "========================================"
