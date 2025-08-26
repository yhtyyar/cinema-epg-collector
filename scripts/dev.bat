@echo off
echo ========================================
echo   IPTV EPG Collector - Режим разработки
echo ========================================
echo.

REM Проверка Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Docker не установлен или не запущен
    pause
    exit /b 1
)

echo [INFO] Запускаем в режиме разработки...
docker-compose -f docker-compose.dev.yml up -d

if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось запустить контейнеры
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Режим разработки запущен!
echo.
echo Frontend (Vite): http://localhost:5173
echo Backend API:     http://localhost:8000
echo API Docs:        http://localhost:8000/docs
echo.
echo Для просмотра логов: docker-compose -f docker-compose.dev.yml logs -f
echo Для остановки: docker-compose -f docker-compose.dev.yml down
echo ========================================
pause
