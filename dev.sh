#!/bin/bash

# Development helper script for automatic-mailgun

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build Docker image"
    echo "  run         Run with Docker Compose"
    echo "  test        Run tests"
    echo "  lint        Run linting"
    echo "  clean       Clean up Docker resources"
    echo "  dev         Run in development mode (local Python)"
    echo "  help        Show this help message"
}

build() {
    echo -e "${GREEN}Building Docker image...${NC}"
    docker build -t automatic-mailgun .
}

run() {
    echo -e "${GREEN}Starting application with Docker Compose...${NC}"
    docker-compose up --build
}

test() {
    echo -e "${GREEN}Running tests...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    pip install -r requirements.txt
    pip install pytest pytest-cov flake8
    python -m pytest tests/ -v
}

lint() {
    echo -e "${GREEN}Running linting...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    pip install flake8
    flake8 src/ --max-line-length=127 --exclude=__pycache__
}

clean() {
    echo -e "${GREEN}Cleaning up Docker resources...${NC}"
    docker-compose down --volumes --remove-orphans
    docker system prune -f
}

dev() {
    echo -e "${GREEN}Starting development server...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    pip install -r requirements.txt
    cd src && python main.py
}

case "$1" in
    build)
        build
        ;;
    run)
        run
        ;;
    test)
        test
        ;;
    lint)
        lint
        ;;
    clean)
        clean
        ;;
    dev)
        dev
        ;;
    help|"")
        print_usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        print_usage
        exit 1
        ;;
esac
