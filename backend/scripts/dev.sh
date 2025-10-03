#!/bin/bash

# Development server startup script using Uvicorn
# Usage: ./scripts/dev.sh [host] [port]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}Starting GarageReg API Development Server${NC}"
echo "Project root: $PROJECT_ROOT"

# Change to project directory
cd "$PROJECT_ROOT"

# Default values
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8000"
HOST=${1:-$DEFAULT_HOST}
PORT=${2:-$DEFAULT_PORT}

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment from .env${NC}"
    export $(grep -v '^#' .env | xargs)
fi

# Override with command line arguments
export HOST="$HOST"
export PORT="$PORT"

echo "Starting server on http://$HOST:$PORT"
echo "Docs available at: http://$HOST:$PORT/docs"
echo "Health check: http://$HOST:$PORT/healthz"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start uvicorn with development settings
uvicorn app.main:app \
    --host "$HOST" \
    --port "$PORT" \
    --reload \
    --reload-dir app \
    --reload-exclude "*.pyc" \
    --reload-exclude "*.pyo" \
    --reload-exclude "*.pyd" \
    --reload-exclude "__pycache__" \
    --log-level info \
    --access-log \
    --use-colors \
    --loop uvloop