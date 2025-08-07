#!/bin/bash

# CinemaEPGCollector Server Setup Script
# Устанавливает все необходимые компоненты на Ubuntu/Debian сервер

set -e

echo "🚀 Starting CinemaEPGCollector server setup..."

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

# Проверка прав sudo
if ! sudo -n true 2>/dev/null; then
    print_error "This script requires sudo privileges"
    exit 1
fi

# 1. Обновление системы
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Установка базовых пакетов
print_status "Installing basic packages..."
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# 3. Установка Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed successfully"
else
    print_warning "Docker is already installed"
fi

# 4. Установка Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_warning "Docker Compose is already installed"
fi

# 5. Установка Go
print_status "Installing Go..."
GO_VERSION="1.21.6"
if ! command -v go &> /dev/null; then
    wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz
    rm go${GO_VERSION}.linux-amd64.tar.gz
    
    # Добавление в PATH
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    echo 'export GOPATH=$HOME/go' >> ~/.bashrc
    echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
    
    export PATH=$PATH:/usr/local/go/bin
    export GOPATH=$HOME/go
    export PATH=$PATH:$GOPATH/bin
    
    print_status "Go ${GO_VERSION} installed successfully"
else
    print_warning "Go is already installed"
fi

# 6. Создание директорий проекта
print_status "Creating project directories..."
mkdir -p ~/projects
mkdir -p ~/logs

# 7. Настройка firewall (опционально)
print_status "Configuring firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 8080/tcp
    sudo ufw allow 22/tcp
    print_status "Firewall configured (ports 8080, 22 opened)"
fi

# 8. Запуск Docker
print_status "Starting Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

# 9. Проверка установки
print_status "Verifying installation..."
echo "Docker version:"
docker --version
echo "Docker Compose version:"
docker-compose --version
echo "Go version:"
/usr/local/go/bin/go version

print_status "✅ Server setup completed successfully!"
print_warning "⚠️  Please logout and login again to apply Docker group changes"
print_status "Next steps:"
echo "1. Copy your project to ~/projects/"
echo "2. cd ~/projects/cinema-epg-collector"
echo "3. docker-compose up -d postgres redis"
echo "4. go mod tidy"
echo "5. go run cmd/server/main.go"
