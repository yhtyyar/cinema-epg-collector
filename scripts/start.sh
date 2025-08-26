#!/bin/bash

echo "========================================"
echo "  IPTV EPG Collector - Запуск проекта"
echo "========================================"
echo

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "[ОШИБКА] Docker не установлен"
    echo "Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "[ОШИБКА] Docker Compose не установлен"
    echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "[INFO] Docker проверен успешно"
echo

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "[ВНИМАНИЕ] Файл .env не найден"
    echo "Копируем .env.example в .env..."
    cp .env.example .env
    echo "[INFO] Файл .env создан. Отредактируйте его при необходимости."
    echo
fi

echo "[INFO] Запускаем контейнеры..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось запустить контейнеры"
    echo "Проверьте логи: docker-compose logs"
    exit 1
fi

echo
echo "[SUCCESS] Контейнеры запущены!"
echo

echo "Проверяем статус..."
docker-compose ps

echo
echo "========================================"
echo "  Приложение готово к использованию!"
echo "========================================"
echo
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo
echo "Для загрузки данных выполните:"
echo "docker-compose exec backend python -m epg_collector.cli run-all"
echo
echo "Для остановки: docker-compose down"
echo "========================================"
