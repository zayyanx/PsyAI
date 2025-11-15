# PsyAI Platform - VM Setup Guide

Complete guide to set up and test the PsyAI platform in a VM environment.

## Prerequisites

- Ubuntu 20.04+ or Debian-based Linux
- Python 3.9+
- 2GB+ RAM
- Internet connection

## Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd PsyAI

# Run automated setup script
bash scripts/setup_vm.sh

# Start services
docker-compose up -d

# Activate virtual environment
source venv/bin/activate

# Initialize database
alembic upgrade head

# Run the API server
uvicorn psyai.platform.api_framework:app --host 0.0.0.0 --port 8000 --reload
```

## Manual Setup

### 1. System Dependencies

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and build tools
sudo apt-get install -y python3.9 python3.9-venv python3-pip
sudo apt-get install -y build-essential libpq-dev

# Install Docker and Docker Compose
sudo apt-get install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 2. Python Environment

```bash
# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -e .
pip install -r requirements.txt
```

### 3. Database & Cache Services

```bash
# Start PostgreSQL and Redis using Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps

# Check PostgreSQL
docker exec psyai-postgres psql -U psyai -d psyai -c "SELECT version();"

# Check Redis
docker exec psyai-redis redis-cli ping
```

### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (use your preferred editor)
nano .env
```

Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_HOST` - Redis hostname (default: localhost)
- `SECRET_KEY` - JWT secret key (generate a secure random string)
- `LANGSMITH_API_KEY` - LangSmith API key
- `CENTAUR_API_KEY` - Centaur API key (if available)

### 5. Database Migration

```bash
# Initialize database schema
alembic upgrade head

# Verify tables were created
docker exec psyai-postgres psql -U psyai -d psyai -c "\dt"
```

### 6. Run the API Server

```bash
# Development mode with auto-reload
uvicorn psyai.platform.api_framework:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn psyai.platform.api_framework:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing the API

### Health Check

```bash
# Basic health check
curl http://localhost:8000/api/v1/health

# Detailed health check
curl http://localhost:8000/api/v1/health/detailed

# Ping
curl http://localhost:8000/api/v1/ping
```

### User Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

### User Login

```bash
# Login to get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=SecurePass123!"

# Or use JSON login
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### Authenticated Requests

```bash
# Export token (replace with your actual token)
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get current user info
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# Create chat session
curl -X POST http://localhost:8000/api/v1/chat/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ai",
    "title": "Test Chat Session"
  }'

# Send message (replace {session_id} with actual ID)
curl -X POST http://localhost:8000/api/v1/chat/sessions/{session_id}/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello, AI!"
  }'
```

### Automated Testing

```bash
# Run the test script
python scripts/test_api.py

# Or run unit tests
pytest tests/ -v

# Run specific test categories
pytest tests/platform/api_framework/ -v
pytest tests/platform/storage_layer/ -v
```

## API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Redis Connection Issues

```bash
# Check Redis is running
docker-compose ps redis

# View Redis logs
docker-compose logs redis

# Test Redis connection
docker exec psyai-redis redis-cli ping
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Migration Issues

```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

## Performance Testing

```bash
# Install Apache Bench
sudo apt-get install -y apache2-utils

# Test health endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/api/v1/health

# Load test with authentication
# First get a token, then:
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/users/me
```

## Monitoring

### View Application Logs

```bash
# Real-time logs
tail -f logs/psyai.log

# Search for errors
grep ERROR logs/psyai.log

# View structured logs
cat logs/psyai.log | jq .
```

### Database Monitoring

```bash
# Check active connections
docker exec psyai-postgres psql -U psyai -d psyai -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Check database size
docker exec psyai-postgres psql -U psyai -d psyai -c \
  "SELECT pg_size_pretty(pg_database_size('psyai'));"
```

### Redis Monitoring

```bash
# Get Redis stats
docker exec psyai-redis redis-cli info stats

# Monitor commands in real-time
docker exec psyai-redis redis-cli monitor
```

## Clean Up

```bash
# Stop services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Deactivate virtual environment
deactivate
```

## Production Deployment

For production deployment, consider:

1. **Use HTTPS**: Set up SSL/TLS certificates (Let's Encrypt)
2. **Environment Variables**: Use secrets management (AWS Secrets Manager, HashiCorp Vault)
3. **Database**: Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
4. **Cache**: Use managed Redis (AWS ElastiCache, Redis Cloud)
5. **Reverse Proxy**: Use nginx or Caddy
6. **Process Manager**: Use systemd or supervisor
7. **Container Orchestration**: Consider Kubernetes or AWS ECS
8. **Monitoring**: Set up Prometheus + Grafana or DataDog
9. **Logging**: Use centralized logging (ELK stack, Cloudwatch)
10. **Backups**: Automated database backups

## Security Checklist

- [ ] Change default `SECRET_KEY` to a secure random string
- [ ] Use strong database passwords
- [ ] Enable firewall and restrict port access
- [ ] Keep dependencies updated (`pip list --outdated`)
- [ ] Enable HTTPS in production
- [ ] Implement rate limiting
- [ ] Regular security audits
- [ ] Monitor for suspicious activity

## Support

For issues or questions:
- Check the troubleshooting section above
- Review application logs
- Open an issue on GitHub
- Consult the API documentation at `/docs`
