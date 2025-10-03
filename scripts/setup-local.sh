#!/bin/bash
# =============================================================================
# GARAGEREG LOCAL ENVIRONMENT SETUP SCRIPT
# Complete setup for local development environment
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INFRA_DIR="$PROJECT_ROOT/infra"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

# Check if running on Windows (Git Bash/WSL)
is_windows() {
    [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -n "${WSL_DISTRO_NAME:-}" ]]
}

# Function to check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    else
        log_success "Docker found: $(docker --version)"
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        missing_tools+=("docker-compose")
    else
        log_success "Docker Compose found: $(docker compose version)"
    fi
    
    # Check OpenSSL
    if ! command -v openssl &> /dev/null; then
        missing_tools+=("openssl")
    else
        log_success "OpenSSL found: $(openssl version)"
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    else
        log_success "Git found: $(git --version)"
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install the missing tools and run this script again."
        exit 1
    fi
    
    log_success "All prerequisites satisfied!"
}

# Function to setup environment file
setup_environment() {
    log_step "Setting up environment configuration..."
    
    local env_file="$INFRA_DIR/.env"
    local env_example="$INFRA_DIR/.env.example"
    
    if [[ ! -f "$env_example" ]]; then
        log_error "Environment example file not found: $env_example"
        exit 1
    fi
    
    if [[ -f "$env_file" ]]; then
        log_warning "Environment file already exists: $env_file"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Keeping existing environment file."
            return
        fi
    fi
    
    cp "$env_example" "$env_file"
    
    # Generate secure random passwords
    log_info "Generating secure passwords..."
    
    local db_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    local redis_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    local secret_key=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
    
    # Update passwords in environment file
    if is_windows; then
        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$db_password/" "$env_file"
        sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$redis_password/" "$env_file"
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$secret_key/" "$env_file"
    else
        sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=$db_password/" "$env_file"
        sed -i.bak "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$redis_password/" "$env_file"
        sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$secret_key/" "$env_file"
        rm -f "$env_file.bak"
    fi
    
    log_success "Environment file created with secure passwords!"
}

# Function to generate TLS certificates
generate_certificates() {
    log_step "Generating TLS certificates..."
    
    local cert_script="$INFRA_DIR/traefik/generate-certs.sh"
    
    if [[ ! -f "$cert_script" ]]; then
        log_error "Certificate generation script not found: $cert_script"
        exit 1
    fi
    
    # Make script executable
    chmod +x "$cert_script"
    
    # Run certificate generation
    if is_windows; then
        log_info "Running certificate generation in Git Bash..."
        bash "$cert_script"
    else
        "$cert_script"
    fi
    
    log_success "TLS certificates generated!"
}

# Function to setup hosts file
setup_hosts() {
    log_step "Setting up hosts file entries..."
    
    local domains=(
        "garagereg.local"
        "api.garagereg.local"
        "admin.garagereg.local"
        "app.garagereg.local"
        "traefik.garagereg.local"
        "mail.garagereg.local"
        "metrics.garagereg.local"
        "dashboard.garagereg.local"
        "mobile-api.garagereg.local"
    )
    
    local hosts_entry="127.0.0.1"
    
    if is_windows; then
        local hosts_file="/c/Windows/System32/drivers/etc/hosts"
        if [[ -f "$hosts_file" ]]; then
            log_warning "Windows hosts file modification requires administrator privileges."
            log_info "Please add the following entries to your hosts file manually:"
            log_info "File location: C:\\Windows\\System32\\drivers\\etc\\hosts"
        else
            log_warning "Cannot access Windows hosts file. Please add entries manually."
        fi
    else
        local hosts_file="/etc/hosts"
        if [[ -w "$hosts_file" ]] || command -v sudo &> /dev/null; then
            log_info "Adding entries to hosts file..."
            for domain in "${domains[@]}"; do
                if ! grep -q "$domain" "$hosts_file"; then
                    if [[ -w "$hosts_file" ]]; then
                        echo "$hosts_entry $domain" >> "$hosts_file"
                    else
                        echo "$hosts_entry $domain" | sudo tee -a "$hosts_file" > /dev/null
                    fi
                    log_info "Added: $hosts_entry $domain"
                fi
            done
            log_success "Hosts file updated!"
        else
            log_warning "Cannot modify hosts file. Please add entries manually:"
        fi
    fi
    
    # Always show the entries for manual addition
    echo ""
    log_info "Required hosts file entries:"
    echo -e "${CYAN}# GarageReg Local Development${NC}"
    for domain in "${domains[@]}"; do
        echo -e "${CYAN}$hosts_entry $domain${NC}"
    done
    echo ""
}

# Function to build and start services
start_services() {
    log_step "Building and starting services..."
    
    cd "$INFRA_DIR"
    
    # Load environment variables
    if [[ -f ".env" ]]; then
        set -a
        source .env
        set +a
    fi
    
    # Pull latest images
    log_info "Pulling latest Docker images..."
    docker compose pull
    
    # Build custom images
    log_info "Building custom images..."
    docker compose build
    
    # Start services
    log_info "Starting services..."
    docker compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        local healthy_services=0
        local total_services=0
        
        # Check each service
        for service in traefik postgres redis; do
            total_services=$((total_services + 1))
            if docker compose ps "$service" --format json | jq -e '.Health == "healthy" or .State == "running"' > /dev/null 2>&1; then
                healthy_services=$((healthy_services + 1))
            fi
        done
        
        if [[ $healthy_services -eq $total_services ]]; then
            log_success "All services are healthy!"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            log_error "Services did not become healthy within expected time."
            log_info "Current service status:"
            docker compose ps
            return 1
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
    
    log_success "Services started successfully!"
}

# Function to run database migrations
run_migrations() {
    log_step "Running database migrations..."
    
    cd "$INFRA_DIR"
    
    # Wait a bit more for database to be fully ready
    sleep 5
    
    # Run migrations
    if docker compose exec -T backend alembic upgrade head; then
        log_success "Database migrations completed!"
    else
        log_warning "Database migrations failed or backend service not ready."
        log_info "You can run migrations later with:"
        log_info "  docker compose -f infra/docker-compose.yml exec backend alembic upgrade head"
    fi
}

# Function to create initial data
create_initial_data() {
    log_step "Creating initial test data..."
    
    cd "$INFRA_DIR"
    
    # Create initial data
    if docker compose exec -T backend python create_simple_test_data.py; then
        log_success "Initial test data created!"
    else
        log_warning "Initial data creation failed or backend service not ready."
        log_info "You can create test data later with:"
        log_info "  docker compose -f infra/docker-compose.yml exec backend python create_simple_test_data.py"
    fi
}

# Function to display access information
show_access_info() {
    log_step "Setup completed! Access information:"
    
    echo ""
    echo -e "${GREEN}🎉 GarageReg Local Environment Ready!${NC}"
    echo ""
    echo -e "${CYAN}📱 Applications:${NC}"
    echo -e "  • Admin Interface:    ${YELLOW}https://admin.garagereg.local${NC}"
    echo -e "  • API Documentation:  ${YELLOW}https://api.garagereg.local/docs${NC}"
    echo -e "  • API Redoc:          ${YELLOW}https://api.garagereg.local/redoc${NC}"
    echo ""
    echo -e "${CYAN}🔧 Development Tools:${NC}"
    echo -e "  • Traefik Dashboard:  ${YELLOW}https://traefik.garagereg.local${NC} (admin:admin)"
    echo -e "  • MailHog (Email):    ${YELLOW}https://mail.garagereg.local${NC}"
    echo -e "  • Prometheus:         ${YELLOW}https://metrics.garagereg.local${NC}"
    echo -e "  • Grafana:            ${YELLOW}https://dashboard.garagereg.local${NC} (admin:admin)"
    echo ""
    echo -e "${CYAN}💾 Database Access:${NC}"
    echo -e "  • PostgreSQL:         ${YELLOW}localhost:5432${NC}"
    echo -e "  • Redis:              ${YELLOW}localhost:6379${NC}"
    echo ""
    echo -e "${CYAN}📋 Useful Commands:${NC}"
    echo -e "  • View logs:          ${YELLOW}docker compose -f infra/docker-compose.yml logs -f${NC}"
    echo -e "  • Stop services:      ${YELLOW}docker compose -f infra/docker-compose.yml down${NC}"
    echo -e "  • Restart services:   ${YELLOW}docker compose -f infra/docker-compose.yml restart${NC}"
    echo -e "  • View status:        ${YELLOW}docker compose -f infra/docker-compose.yml ps${NC}"
    echo ""
    echo -e "${CYAN}🛠️ Development:${NC}"
    echo -e "  • Run tests:          ${YELLOW}python scripts/run_tests.py --all${NC}"
    echo -e "  • Backend shell:      ${YELLOW}docker compose -f infra/docker-compose.yml exec backend bash${NC}"
    echo -e "  • Database shell:     ${YELLOW}docker compose -f infra/docker-compose.yml exec postgres psql -U garagereg -d garagereg${NC}"
    echo ""
    echo -e "${GREEN}✨ Happy coding!${NC}"
    echo ""
}

# Function to cleanup on error
cleanup_on_error() {
    log_error "Setup failed. Cleaning up..."
    cd "$INFRA_DIR" 2>/dev/null || true
    docker compose down -v 2>/dev/null || true
}

# Main function
main() {
    echo -e "${GREEN}"
    cat << 'EOF'
 ██████╗  █████╗ ██████╗  █████╗  ██████╗ ███████╗██████╗ ███████╗ ██████╗ 
██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔════╝██╔══██╗██╔════╝██╔════╝ 
██║  ███╗███████║██████╔╝███████║██║  ███╗█████╗  ██████╔╝█████╗  ██║  ███╗
██║   ██║██╔══██║██╔══██╗██╔══██║██║   ██║██╔══╝  ██╔══██╗██╔══╝  ██║   ██║
╚██████╔╝██║  ██║██║  ██║██║  ██║╚██████╔╝███████╗██║  ██║███████╗╚██████╔╝
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ 
                                                                            
                    Local Development Environment Setup                      
EOF
    echo -e "${NC}"
    
    # Set up error handling
    trap cleanup_on_error ERR
    
    log_info "Starting GarageReg local environment setup..."
    
    # Run setup steps
    check_prerequisites
    setup_environment
    generate_certificates
    setup_hosts
    start_services
    run_migrations
    create_initial_data
    show_access_info
    
    log_success "Setup completed successfully!"
}

# Script options
case "${1:-setup}" in
    "setup")
        main
        ;;
    "start")
        log_info "Starting services..."
        cd "$INFRA_DIR"
        docker compose up -d
        log_success "Services started!"
        ;;
    "stop")
        log_info "Stopping services..."
        cd "$INFRA_DIR"
        docker compose down
        log_success "Services stopped!"
        ;;
    "restart")
        log_info "Restarting services..."
        cd "$INFRA_DIR"
        docker compose restart
        log_success "Services restarted!"
        ;;
    "clean")
        log_info "Cleaning up everything..."
        cd "$INFRA_DIR"
        docker compose down -v
        docker system prune -f
        log_success "Cleanup completed!"
        ;;
    "status")
        log_info "Service status:"
        cd "$INFRA_DIR"
        docker compose ps
        ;;
    "logs")
        log_info "Showing logs..."
        cd "$INFRA_DIR"
        docker compose logs -f
        ;;
    "help"|"--help"|"-h")
        echo "GarageReg Local Environment Setup"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup     Complete setup (default)"
        echo "  start     Start services"
        echo "  stop      Stop services"
        echo "  restart   Restart services"
        echo "  clean     Clean up everything"
        echo "  status    Show service status"
        echo "  logs      Show service logs"
        echo "  help      Show this help"
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac