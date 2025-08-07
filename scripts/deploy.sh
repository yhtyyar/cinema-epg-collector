#!/bin/bash

# CinemaEPGCollector Deployment Script
# Разворачивает приложение на сервере

set -e

echo "🚀 Starting CinemaEPGCollector deployment..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия проекта
if [ ! -f "go.mod" ]; then
    print_error "go.mod not found. Please run this script from the project root directory."
    exit 1
fi

# 1. Установка зависимостей
print_status "Installing Go dependencies..."
go mod tidy

# 2. Запуск базы данных и Redis
print_status "Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Ожидание запуска сервисов
print_status "Waiting for services to start..."
sleep 10

# Проверка статуса сервисов
print_status "Checking services status..."
docker-compose ps

# 3. Сборка приложения
print_status "Building application..."
go build -o cinema-epg-collector ./cmd/server

# 4. Создание systemd сервиса (опционально)
create_systemd_service() {
    print_status "Creating systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/cinema-epg-collector.service"
    PROJECT_DIR=$(pwd)
    USER=$(whoami)
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=CinemaEPGCollector Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/cinema-epg-collector
Restart=always
RestartSec=5
Environment=PATH=/usr/local/go/bin:/usr/bin:/bin
Environment=GOPATH=/home/$USER/go

# Логирование
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cinema-epg-collector

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable cinema-epg-collector
    print_status "Systemd service created and enabled"
}

# 5. Запуск приложения
start_application() {
    print_status "Starting CinemaEPGCollector..."
    
    # Проверка, запущен ли уже сервис
    if sudo systemctl is-active --quiet cinema-epg-collector; then
        print_warning "Service is already running. Restarting..."
        sudo systemctl restart cinema-epg-collector
    else
        sudo systemctl start cinema-epg-collector
    fi
    
    # Проверка статуса
    sleep 3
    if sudo systemctl is-active --quiet cinema-epg-collector; then
        print_status "✅ Service started successfully"
        
        # Показать статус
        sudo systemctl status cinema-epg-collector --no-pager -l
        
        # Показать логи
        print_status "Recent logs:"
        sudo journalctl -u cinema-epg-collector -n 20 --no-pager
    else
        print_error "❌ Failed to start service"
        sudo journalctl -u cinema-epg-collector -n 50 --no-pager
        exit 1
    fi
}

# Проверка аргументов командной строки
case "${1:-}" in
    "systemd")
        create_systemd_service
        start_application
        ;;
    "manual")
        print_status "Starting application manually..."
        ./cinema-epg-collector &
        APP_PID=$!
        print_status "Application started with PID: $APP_PID"
        print_status "To stop: kill $APP_PID"
        ;;
    *)
        print_status "Usage: $0 [systemd|manual]"
        print_status "  systemd - Create systemd service and start"
        print_status "  manual  - Start manually in background"
        print_status ""
        print_status "Default: systemd"
        create_systemd_service
        start_application
        ;;
esac

# 6. Проверка работоспособности
print_status "Testing application..."
sleep 5

# Проверка health endpoint
if curl -f -s http://localhost:8080/health > /dev/null; then
    print_status "✅ Health check passed"
    curl -s http://localhost:8080/health | jq . || curl -s http://localhost:8080/health
else
    print_warning "⚠️  Health check failed - service might still be starting"
fi

# Показать полезные команды
print_status "Useful commands:"
echo "  Check status:    sudo systemctl status cinema-epg-collector"
echo "  View logs:       sudo journalctl -u cinema-epg-collector -f"
echo "  Restart:         sudo systemctl restart cinema-epg-collector"
echo "  Stop:            sudo systemctl stop cinema-epg-collector"
echo "  Health check:    curl http://localhost:8080/health"
echo "  Stats:           curl http://localhost:8080/stats"
echo "  Collect playlist: curl -X POST http://localhost:8080/collect/playlist"
echo "  Collect EPG:     curl -X POST http://localhost:8080/collect/epg"

print_status "🎉 Deployment completed!"
