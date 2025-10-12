#!/bin/bash
# GDAI Development Environment Script
# Starts all required services for local development

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# Load environment variables from .env if exists
if [ -f "${PROJECT_ROOT}/.env" ]; then
    echo -e "${BLUE}Loading environment from .env...${NC}"
    set -a  # automatically export all variables
    source "${PROJECT_ROOT}/.env"
    set +a
else
    echo -e "${YELLOW}Warning: .env not found. Using default configuration.${NC}"
    echo -e "${YELLOW}Copy .env.example to .env and configure it for production use.${NC}"
fi

# Change to project root
cd "${PROJECT_ROOT}"

# Function to check if a service is running
check_service() {
    local service_name="$1"
    local port="$2"

    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $service_name is running on port $port"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name is not running on port $port"
        return 1
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local service_name="$1"
    local port="$2"
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}Waiting for $service_name to be ready...${NC}"

    while [ $attempt -lt $max_attempts ]; do
        if nc -z localhost "$port" 2>/dev/null; then
            echo -e "${GREEN}✓ $service_name is ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done

    echo -e "${RED}✗ Timeout waiting for $service_name${NC}"
    return 1
}

# Function to stop all services
cleanup() {
    echo ""
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}  Shutting down services...${NC}"
    echo -e "${YELLOW}========================================${NC}"

    # Kill background processes
    if [ ! -z "$WORKERS_PID" ]; then
        echo -e "${YELLOW}Stopping Temporal workers (PID: $WORKERS_PID)...${NC}"
        kill $WORKERS_PID 2>/dev/null || true
    fi

    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

# Set up cleanup trap
trap cleanup SIGINT SIGTERM EXIT

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  GDAI Development Environment${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Parse command line arguments
START_SERVICES="${1:-all}"

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo -e "${YELLOW}Please install Docker to run infrastructure services${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    echo -e "${YELLOW}Please start Docker and try again${NC}"
    exit 1
fi

# Check docker-compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi

# Use the appropriate docker compose command
DOCKER_COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo -e "${BLUE}Step 1: Starting infrastructure services...${NC}"
echo -e "${CYAN}  • PostgreSQL (pgvector) on port 5555${NC}"
echo -e "${CYAN}  • Temporal Server on port 7233${NC}"
echo -e "${CYAN}  • Temporal UI on port 8233${NC}"
echo -e "${CYAN}  • MinIO on ports 9000 (S3) and 9001 (Console)${NC}"
echo ""

# Check if docker-compose.yaml exists
if [ ! -f "${PROJECT_ROOT}/docker-compose.yaml" ]; then
    echo -e "${RED}Error: docker-compose.yaml not found in project root${NC}"
    exit 1
fi

# Stop all running services before starting (only for infra mode)
if [ "$START_SERVICES" = "infra" ]; then
    echo -e "${YELLOW}Stopping all existing Docker services...${NC}"
    $DOCKER_COMPOSE_CMD -f "${PROJECT_ROOT}/docker-compose.yaml" down 2>/dev/null || true
    echo -e "${GREEN}✓ All services stopped${NC}"
    echo ""
fi

# Start docker-compose services
echo -e "${YELLOW}Running: $DOCKER_COMPOSE_CMD -f ${PROJECT_ROOT}/docker-compose.yaml up -d${NC}"
$DOCKER_COMPOSE_CMD -f "${PROJECT_ROOT}/docker-compose.yaml" up -d

# Wait for services to be ready
echo ""
echo -e "${BLUE}Step 2: Waiting for infrastructure services...${NC}"
wait_for_service "PostgreSQL (pgvector)" 5555
wait_for_service "Temporal Server" 7233
wait_for_service "MinIO" 9000

echo ""
echo -e "${GREEN}✓ Infrastructure services are ready!${NC}"
echo ""

# Initialize database if needed
echo -e "${BLUE}Step 3: Checking database setup...${NC}"
if [ -f "${PROJECT_ROOT}/gdai/scripts/setup_db.py" ]; then
    echo -e "${YELLOW}Running database setup...${NC}"
    uv run python "${PROJECT_ROOT}/gdai/scripts/setup_db.py" || echo -e "${YELLOW}Database setup skipped or already configured${NC}"
else
    echo -e "${YELLOW}Database setup script not found, skipping...${NC}"
fi

echo ""

# Start services based on argument
if [ "$START_SERVICES" = "infra" ]; then
    # Remove trap for infra mode (we don't want to cleanup on exit)
    trap - EXIT

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Infrastructure services started!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${CYAN}Services available:${NC}"
    echo -e "  • PostgreSQL: ${YELLOW}postgresql://testuser:testpwd@localhost:5555/vectordb${NC}"
    echo -e "  • Temporal UI: ${YELLOW}http://localhost:8233${NC}"
    echo -e "  • MinIO Console: ${YELLOW}http://localhost:9001${NC} (minioadmin/minioadmin)"
    echo ""
    echo -e "${BLUE}To stop services, run:${NC} $DOCKER_COMPOSE_CMD -f ${PROJECT_ROOT}/docker-compose.yaml down"
    echo ""
    exit 0
fi

# Start Temporal workers
echo -e "${BLUE}Step 4: Starting Temporal workers...${NC}"
echo -e "${CYAN}  Starting all workflow workers in background...${NC}"
uv run python -m gdai.temporal.main > "${PROJECT_ROOT}/logs/workers.log" 2>&1 &
WORKERS_PID=$!
echo -e "${GREEN}✓ Temporal workers started (PID: $WORKERS_PID)${NC}"
echo -e "${CYAN}  Logs: ${YELLOW}tail -f logs/workers.log${NC}"
sleep 2  # Give workers time to start

echo ""

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Development environment is ready! ✓${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}Available services:${NC}"
echo -e "  • Temporal UI: ${YELLOW}http://localhost:8233${NC}"
echo -e "  • MinIO Console: ${YELLOW}http://localhost:9001${NC} (minioadmin/minioadmin)"
echo -e "  • PostgreSQL: ${YELLOW}postgresql://testuser:testpwd@localhost:5555/vectordb${NC}"
echo ""
echo -e "${CYAN}Logs:${NC}"
echo -e "  • Workers: ${YELLOW}tail -f logs/workers.log${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running and show worker logs
tail -f "${PROJECT_ROOT}/logs/workers.log" 2>/dev/null || wait
