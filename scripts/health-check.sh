#!/bin/bash

# Health check script for GarageReg services
# Usage: ./scripts/health-check.sh [service_name]

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if Docker Compose is running
check_compose_status() {
    if ! docker compose ps > /dev/null 2>&1; then
        print_error "Docker Compose is not running"
        return 1
    fi
}

# Check individual service health
check_service() {
    local service_name=$1
    local service_url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $service_name... "
    
    if curl -s -f -o /dev/null -w "%{http_code}" "$service_url" | grep -q "$expected_status"; then
        print_status "$service_name is healthy"
        return 0
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

# Check database connectivity
check_database() {
    echo -n "Checking database... "
    
    if docker compose exec -T db pg_isready -U garagereg -d garagereg > /dev/null 2>&1; then
        print_status "Database is healthy"
        return 0
    else
        print_error "Database is not responding"
        return 1
    fi
}

# Check Redis connectivity
check_redis() {
    echo -n "Checking Redis... "
    
    if docker compose exec -T redis redis-cli ping | grep -q "PONG"; then
        print_status "Redis is healthy"
        return 0
    else
        print_error "Redis is not responding"
        return 1
    fi
}

# Check MinIO connectivity
check_minio() {
    echo -n "Checking MinIO... "
    
    if curl -s -f "http://localhost:9000/minio/health/live" > /dev/null 2>&1; then
        print_status "MinIO is healthy"
        return 0
    else
        print_error "MinIO is not responding"
        return 1
    fi
}

# Main health check
run_health_check() {
    local service=$1
    local failed=0
    
    echo "🏥 GarageReg Health Check"
    echo "=========================="
    
    # Check Docker Compose status
    if ! check_compose_status; then
        exit 1
    fi
    
    if [ -n "$service" ]; then
        # Check specific service
        case $service in
            "api")
                check_service "API" "http://localhost/api/healthz" || ((failed++))
                ;;
            "web-admin")
                check_service "Web Admin" "http://localhost:3000" || ((failed++))
                ;;
            "db"|"database")
                check_database || ((failed++))
                ;;
            "redis")
                check_redis || ((failed++))
                ;;
            "minio")
                check_minio || ((failed++))
                ;;
            "traefik")
                check_service "Traefik" "http://localhost:8080/api/rawdata" || ((failed++))
                ;;
            "mailhog")
                check_service "Mailhog" "http://localhost:8025" || ((failed++))
                ;;
            *)
                print_error "Unknown service: $service"
                echo "Available services: api, web-admin, db, redis, minio, traefik, mailhog"
                exit 1
                ;;
        esac
    else
        # Check all services
        check_service "API" "http://localhost/api/healthz" || ((failed++))
        check_service "Web Admin" "http://localhost:3000" || ((failed++))
        check_database || ((failed++))
        check_redis || ((failed++))
        check_minio || ((failed++))
        check_service "Traefik" "http://localhost:8080/api/rawdata" || ((failed++))
        check_service "Mailhog" "http://localhost:8025" || ((failed++))
        check_service "Flower" "http://localhost:5555" || ((failed++))
        check_service "Redis Commander" "http://localhost:8081" || ((failed++))
    fi
    
    echo ""
    if [ $failed -eq 0 ]; then
        print_status "All services are healthy! 🎉"
        exit 0
    else
        print_error "$failed service(s) failed health check"
        echo ""
        echo "Troubleshooting:"
        echo "• Check service logs: docker compose logs [service_name]"
        echo "• Restart services: docker compose restart"
        echo "• Full restart: docker compose down && docker compose up -d"
        exit 1
    fi
}

# Show service status
show_status() {
    echo "📊 Service Status"
    echo "=================="
    docker compose ps
    
    echo ""
    echo "💾 Resource Usage"
    echo "=================="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Main execution
case "${1:-health}" in
    "health"|"check")
        run_health_check $2
        ;;
    "status")
        show_status
        ;;
    *)
        echo "Usage: $0 [health|status] [service_name]"
        echo ""
        echo "Commands:"
        echo "  health [service]  - Run health check for all services or specific service"
        echo "  status           - Show service status and resource usage"
        echo ""
        echo "Available services: api, web-admin, db, redis, minio, traefik, mailhog"
        exit 1
        ;;
esac