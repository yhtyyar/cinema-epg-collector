#!/bin/bash

# Cinema EPG Collector - Smart Deployment Script
# Senior Python Developer Best Practices Implementation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="cinema-epg-collector"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                Cinema EPG Collector                          ║"
    echo "║                Senior Python Deployment                      ║"
    echo "║                    Docker Edition                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_dependencies() {
    log_info "Checking system dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "All dependencies are available"
}

setup_environment() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            log_success "Created .env from .env.example"
        else
            log_error ".env.example not found!"
            exit 1
        fi
    else
        log_info ".env file already exists"
    fi
    
    # Check for required TMDB API key
    if ! grep -q "^TMDB_API_KEY=" "$ENV_FILE" || grep -q "^TMDB_API_KEY=$" "$ENV_FILE"; then
        log_warning "TMDB_API_KEY is not set in .env file"
        read -p "Enter your TMDB API key (or press Enter to skip): " tmdb_key
        if [ ! -z "$tmdb_key" ]; then
            sed -i "s/^TMDB_API_KEY=.*/TMDB_API_KEY=$tmdb_key/" "$ENV_FILE"
            log_success "TMDB API key updated"
        fi
    fi
}

create_directories() {
    log_info "Creating required directories..."
    
    mkdir -p data/posters
    mkdir -p cache
    mkdir -p logs
    
    log_success "Directories created"
}

build_and_deploy() {
    local mode=${1:-"development"}
    
    log_info "Building and deploying in $mode mode..."
    
    # Stop existing containers
    if docker-compose ps | grep -q "Up"; then
        log_info "Stopping existing containers..."
        docker-compose down
    fi
    
    # Build and start services
    case $mode in
        "development"|"dev")
            log_info "Starting in development mode..."
            docker-compose up --build -d
            ;;
        "production"|"prod")
            log_info "Starting in production mode..."
            docker-compose --profile production up --build -d
            ;;
        "frontend")
            log_info "Starting with frontend..."
            docker-compose --profile frontend up --build -d
            ;;
        *)
            log_error "Unknown mode: $mode"
            exit 1
            ;;
    esac
    
    log_success "Deployment completed in $mode mode"
}

show_status() {
    log_info "Service Status:"
    docker-compose ps
    
    echo ""
    log_info "Service Logs (last 20 lines):"
    docker-compose logs --tail=20
    
    echo ""
    log_info "Available endpoints:"
    echo "  🌐 API: http://localhost:8000"
    echo "  📚 API Docs: http://localhost:8000/docs"
    echo "  🏥 Health Check: http://localhost:8000/healthz"
    echo "  📊 Movies API: http://localhost:8000/api/movies"
}

run_pipeline() {
    log_info "Running data collection pipeline manually..."
    
    docker-compose exec cinema-epg-api python -m epg_collector.cli run-all
    
    log_success "Pipeline execution completed"
}

cleanup() {
    log_info "Cleaning up Docker resources..."
    
    docker-compose down -v
    docker system prune -f
    
    log_success "Cleanup completed"
}

show_help() {
    echo "Cinema EPG Collector - Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  deploy [mode]     Deploy the application (modes: dev, prod, frontend)"
    echo "  status            Show service status and logs"
    echo "  pipeline          Run data collection pipeline manually"
    echo "  stop              Stop all services"
    echo "  restart           Restart all services"
    echo "  logs [service]    Show logs for specific service or all"
    echo "  cleanup           Stop services and clean up Docker resources"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy dev     # Deploy in development mode"
    echo "  $0 deploy prod    # Deploy in production mode"
    echo "  $0 status         # Show current status"
    echo "  $0 pipeline       # Run data collection"
    echo ""
}

# Main execution
main() {
    print_banner
    
    case ${1:-"deploy"} in
        "deploy")
            check_dependencies
            setup_environment
            create_directories
            build_and_deploy ${2:-"development"}
            show_status
            ;;
        "status")
            show_status
            ;;
        "pipeline")
            run_pipeline
            ;;
        "stop")
            log_info "Stopping all services..."
            docker-compose down
            log_success "All services stopped"
            ;;
        "restart")
            log_info "Restarting all services..."
            docker-compose restart
            log_success "All services restarted"
            ;;
        "logs")
            if [ ! -z "$2" ]; then
                docker-compose logs -f "$2"
            else
                docker-compose logs -f
            fi
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
