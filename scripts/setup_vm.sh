#!/bin/bash

set -e  # Exit on error

echo "========================================="
echo "PsyAI Platform - VM Setup Script"
echo "========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Step 1: Update system packages
print_info "Updating system packages..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq
print_success "System packages updated"

# Step 2: Install system dependencies
print_info "Installing system dependencies..."
sudo apt-get install -y -qq \
    python3.9 \
    python3.9-venv \
    python3-pip \
    build-essential \
    libpq-dev \
    curl \
    git \
    jq
print_success "System dependencies installed"

# Step 3: Install Docker
if ! command -v docker &> /dev/null; then
    print_info "Installing Docker..."
    sudo apt-get install -y -qq docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    print_success "Docker installed"
else
    print_success "Docker already installed"
fi

# Step 4: Create Python virtual environment
print_info "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3.9 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Step 5: Activate virtual environment and install Python dependencies
print_info "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel -q
pip install -e . -q

# Install additional dev dependencies
pip install -q \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy \
    httpx \
    uvicorn

print_success "Python dependencies installed"

# Step 6: Create environment file
print_info "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    
    # Generate a secure SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    
    print_success "Environment file created (.env)"
    print_info "Please update .env with your API keys"
else
    print_success "Environment file already exists"
fi

# Step 7: Start Docker services
print_info "Starting PostgreSQL and Redis services..."
docker-compose up -d postgres redis
sleep 5  # Wait for services to start
print_success "Database and cache services started"

# Step 8: Check service health
print_info "Checking service health..."

# Check PostgreSQL
if docker exec psyai-postgres pg_isready -U psyai -d psyai > /dev/null 2>&1; then
    print_success "PostgreSQL is healthy"
else
    print_error "PostgreSQL health check failed"
fi

# Check Redis
if docker exec psyai-redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is healthy"
else
    print_error "Redis health check failed"
fi

# Step 9: Run database migrations
print_info "Running database migrations..."
alembic upgrade head
print_success "Database schema initialized"

# Step 10: Run tests
print_info "Running tests..."
if pytest tests/ -v --tb=short > /tmp/test_results.log 2>&1; then
    print_success "All tests passed!"
else
    print_error "Some tests failed. Check /tmp/test_results.log for details"
fi

echo
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo
echo "To start the API server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: uvicorn psyai.platform.api_framework:app --reload"
echo
echo "Access the API documentation at:"
echo "  - http://localhost:8000/docs (Swagger UI)"
echo "  - http://localhost:8000/redoc (ReDoc)"
echo
echo "To run tests:"
echo "  pytest tests/ -v"
echo
echo "To view logs:"
echo "  docker-compose logs -f"
echo
