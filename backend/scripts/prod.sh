#!/bin/bash

# Production server startup script using Gunicorn
# Usage: ./scripts/prod.sh [workers] [port]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}Starting GarageReg API Production Server${NC}"

# Change to project directory
cd "$PROJECT_ROOT"

# Default values
DEFAULT_WORKERS="4"
DEFAULT_PORT="8000"
DEFAULT_HOST="0.0.0.0"

WORKERS=${1:-$DEFAULT_WORKERS}
PORT=${2:-$DEFAULT_PORT}
HOST=${HOST:-$DEFAULT_HOST}

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment from .env${NC}"
    export $(grep -v '^#' .env | xargs)
fi

# Validate environment
if [ "$APP_ENV" != "production" ] && [ "$APP_ENV" != "staging" ]; then
    echo -e "${RED}Warning: APP_ENV is not set to production or staging${NC}"
    echo "Current APP_ENV: ${APP_ENV:-not set}"
fi

# Calculate workers if not specified
if [ "$WORKERS" = "auto" ]; then
    CPU_COUNT=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
    WORKERS=$((CPU_COUNT * 2 + 1))
    echo "Auto-detected $CPU_COUNT CPUs, using $WORKERS workers"
fi

echo "Configuration:"
echo "  Host: $HOST"
echo "  Port: $PORT" 
echo "  Workers: $WORKERS"
echo "  Environment: ${APP_ENV:-development}"
echo "  Log Level: ${LOG_LEVEL:-INFO}"
echo ""

# Create necessary directories
mkdir -p logs
mkdir -p pids

# Gunicorn configuration
GUNICORN_CONF="scripts/gunicorn.conf.py"

# Start gunicorn
echo -e "${GREEN}Starting Gunicorn...${NC}"

exec gunicorn app.main:app \
    --bind "$HOST:$PORT" \
    --workers "$WORKERS" \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --timeout 30 \
    --keepalive 5 \
    --graceful-timeout 30 \
    --pid pids/gunicorn.pid \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level "${LOG_LEVEL:-info}" \
    --capture-output \
    --enable-stdio-inheritance