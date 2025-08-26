@echo off
echo ========================================
echo   IPTV EPG Collector - Запуск проекта
echo ========================================
echo.

REM Проверка Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Docker не установлен или не запущен
    echo Установите Docker Desktop: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Docker Compose не доступен
    pause
    exit /b 1
)

echo [INFO] Docker проверен успешно
echo.

REM Проверка .env файла
if not exist ".env" (
    echo [ВНИМАНИЕ] Файл .env не найден
    echo Копируем .env.example в .env...
    copy .env.example .env >nul
    echo [INFO] Файл .env создан. Отредактируйте его при необходимости.
    echo.
)

echo [INFO] Запускаем контейнеры...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось запустить контейнеры
    echo Проверьте логи: docker-compose logs
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Контейнеры запущены!
echo.
echo Проверяем статус...
docker-compose ps

echo.
echo ========================================
echo   Приложение готово к использованию!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Для загрузки данных выполните:
echo docker-compose exec backend python -m epg_collector.cli run-all
echo.
echo Для остановки: docker-compose down
echo ========================================
pause
