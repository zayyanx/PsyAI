# PsyAI Platform - Scripts

This directory contains utility scripts for setting up and testing the PsyAI platform.

## Available Scripts

### setup_vm.sh
Automated VM setup script that installs all dependencies and configures the environment.

**Usage:**
```bash
bash scripts/setup_vm.sh
```

**What it does:**
1. Updates system packages
2. Installs Python 3.9 and build tools
3. Installs Docker and Docker Compose
4. Creates Python virtual environment
5. Installs Python dependencies
6. Generates environment configuration (.env)
7. Starts PostgreSQL and Redis containers
8. Runs database migrations
9. Executes test suite

**Requirements:**
- Ubuntu 20.04+ or Debian-based Linux
- sudo privileges
- Internet connection

---

### test_api.py
Comprehensive API testing script that validates all endpoints.

**Usage:**
```bash
# Basic usage (default: http://localhost:8000)
python scripts/test_api.py

# Custom API URL
python scripts/test_api.py --url http://localhost:8000
```

**What it tests:**
- Health endpoints (/health, /ping)
- Authentication (register, login)
- User management (get, update)
- Chat sessions (create, list, messages)

**Output:**
- Colored terminal output showing pass/fail for each test
- Response times for each endpoint
- Summary statistics (total, passed, failed, pass rate)

**Requirements:**
- API server must be running
- Python requests library installed

---

## Quick Start

1. **Set up the VM:**
   ```bash
   bash scripts/setup_vm.sh
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Start the API server:**
   ```bash
   uvicorn psyai.platform.api_framework:app --reload
   ```

4. **Run API tests (in another terminal):**
   ```bash
   python scripts/test_api.py
   ```

---

## Development Workflow

### Initial Setup
```bash
# Clone and setup
git clone <repo-url>
cd PsyAI
bash scripts/setup_vm.sh
```

### Daily Development
```bash
# Start services
docker-compose up -d

# Activate environment
source venv/bin/activate

# Run server
uvicorn psyai.platform.api_framework:app --reload

# In another terminal, run tests
python scripts/test_api.py
```

### Before Committing
```bash
# Run all tests
pytest tests/ -v

# Check code formatting
black src/ tests/
flake8 src/ tests/

# Run type checking
mypy src/
```

---

## Troubleshooting

### Script Permission Denied
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### Virtual Environment Not Activated
```bash
source venv/bin/activate
# You should see (venv) in your prompt
```

### Docker Permission Denied
```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

### Port Already in Use
```bash
# Find process using port 8000
sudo lsof -i :8000
# Kill the process
sudo kill -9 <PID>
```

---

## Additional Scripts (Coming Soon)

- `backup_db.sh` - Database backup utility
- `deploy.sh` - Production deployment script
- `load_test.py` - Performance testing script
- `generate_docs.sh` - API documentation generator

---

## Contributing

When adding new scripts:
1. Make scripts executable: `chmod +x script.sh`
2. Add proper error handling
3. Include usage documentation
4. Update this README
5. Test thoroughly before committing
