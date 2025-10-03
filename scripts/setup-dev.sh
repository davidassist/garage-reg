#!/bin/bash

# GarageReg Development Setup Script
# This script sets up the entire development environment

set -e

echo "🚀 Setting up GarageReg development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_status "Docker is running ✓"
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    print_status "Docker Compose is available ✓"
}

# Setup environment files
setup_env_files() {
    print_status "Setting up environment files..."
    
    # Root .env
    if [ ! -f .env ]; then
        cp .env.example .env
        print_status "Created .env from .env.example"
    else
        print_warning ".env already exists, skipping..."
    fi
    
    # Web admin .env.local
    if [ ! -f web-admin/.env.local ]; then
        cp web-admin/.env.example web-admin/.env.local
        print_status "Created web-admin/.env.local"
    else
        print_warning "web-admin/.env.local already exists, skipping..."
    fi
    
    # Mobile .env
    if [ ! -f mobile/.env ]; then
        cp mobile/.env.example mobile/.env
        print_status "Created mobile/.env"
    else
        print_warning "mobile/.env already exists, skipping..."
    fi
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    docker compose build
    print_status "Docker images built successfully ✓"
}

# Start services
start_services() {
    print_status "Starting services..."
    docker compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
}

# Check service health
check_service_health() {
    print_status "Checking service health..."
    
    # Check API health
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost/api/healthz > /dev/null 2>&1; then
            print_status "API is healthy ✓"
            break
        else
            if [ $attempt -eq $max_attempts ]; then
                print_error "API health check failed after $max_attempts attempts"
                docker compose logs api
                exit 1
            fi
            print_warning "API not ready yet, attempt $attempt/$max_attempts..."
            sleep 10
            ((attempt++))
        fi
    done
    
    # Check other services
    services=("db" "redis" "minio" "mailhog" "traefik")
    for service in "${services[@]}"; do
        if docker compose ps $service | grep -q "healthy\|running"; then
            print_status "$service is running ✓"
        else
            print_warning "$service may not be fully ready"
        fi
    done
}

# Install backend dependencies
setup_backend() {
    print_status "Setting up backend dependencies..."
    
    if command -v python3 > /dev/null 2>&1; then
        cd backend
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            print_status "Created Python virtual environment"
        fi
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
        pip install -r requirements.txt
        print_status "Backend dependencies installed ✓"
        
        cd ..
    else
        print_warning "Python3 not found, skipping backend setup"
    fi
}

# Install frontend dependencies
setup_frontend() {
    print_status "Setting up frontend dependencies..."
    
    if command -v npm > /dev/null 2>&1; then
        cd web-admin
        npm install
        print_status "Frontend dependencies installed ✓"
        cd ..
    else
        print_warning "npm not found, skipping frontend setup"
    fi
}

# Setup mobile dependencies
setup_mobile() {
    print_status "Setting up mobile dependencies..."
    
    if command -v flutter > /dev/null 2>&1; then
        cd mobile
        flutter pub get
        print_status "Mobile dependencies installed ✓"
        cd ..
    else
        print_warning "Flutter not found, skipping mobile setup"
    fi
}

# Show service URLs
show_service_info() {
    print_status "🎉 Setup completed successfully!"
    echo ""
    echo "Service URLs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 API:              http://localhost/api"
    echo "📊 API Docs:         http://localhost/api/docs"
    echo "💻 Web Admin:        http://localhost:3000"
    echo "📧 Mailhog:          http://localhost:8025"
    echo "🗂️  MinIO Console:    http://localhost:9001"
    echo "🔄 Traefik Dashboard: http://localhost:8080"
    echo "📊 Flower (Celery):   http://localhost:5555"
    echo "🔴 Redis Commander:   http://localhost:8081"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Default credentials:"
    echo "• MinIO: minioadmin / minioadmin"
    echo "• Database: garagereg / garagereg_dev_password"
    echo ""
    echo "To view logs: docker compose logs -f [service]"
    echo "To stop: docker compose down"
}

# Main execution
main() {
    print_status "Starting GarageReg development setup..."
    
    check_docker
    check_docker_compose
    setup_env_files
    build_images
    start_services
    
    # Optional: Setup local development dependencies
    read -p "Do you want to set up local development dependencies? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_backend
        setup_frontend
        setup_mobile
    fi
    
    show_service_info
}

# Run main function
main "$@"