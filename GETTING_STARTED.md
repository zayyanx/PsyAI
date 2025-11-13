# Getting Started with PsyAI

## Quick Overview

PsyAI is structured into **Platform** (serial) and **Features** (parallel):

```
Platform (Serial - 8 weeks)          Features (Parallel - 4 weeks)
┌────────────────────────┐          ┌─────────────────────────┐
│ 1. Core Infrastructure │          │ • Chat                  │
│ 2. LangChain/LangGraph │   →→→    │ • Evals                 │
│ 3. LangSmith           │          │ • Human-in-the-Loop     │
│ 4. Centaur Model       │          │ • Confidence Score      │
│ 5. Storage Layer       │          │                         │
│ 6. API Framework       │          │ (Built in parallel)     │
└────────────────────────┘          └─────────────────────────┘
```

## Repository Structure

```
PsyAI/
├── ARCHITECTURE.md           # System architecture and components
├── ROADMAP.md               # Detailed build plan and timeline
├── GETTING_STARTED.md       # This file
│
├── src/psyai/
│   ├── core/                # Platform Layer 1 (Core Infrastructure)
│   ├── platform/            # Platform Layers 2-6
│   │   ├── langchain_integration/
│   │   ├── langsmith_integration/
│   │   ├── centaur_integration/
│   │   ├── storage/
│   │   └── api/
│   └── features/            # Feature Layer (Parallel)
│       ├── chat/
│       ├── evals/
│       ├── hitl/
│       └── confidence/
│
├── tests/
├── docs/
├── scripts/
└── docker/
```

## For Developers

### Initial Setup

1. **Clone and set up environment:**
```bash
git clone https://github.com/zayyanx/PsyAI.git
cd PsyAI
bash scripts/setup_dev.sh
```

2. **Configure environment:**
```bash
# Edit .env with your API keys
vi .env

# Required keys:
# - OPENAI_API_KEY
# - LANGSMITH_API_KEY
# - CENTAUR_API_KEY (when available)
```

3. **Start services:**
```bash
cd docker
docker-compose up -d postgres redis
```

### Current Status

**Phase:** Initial Structure Setup
**Next:** Begin Platform Development (Sprint 1 - Core Infrastructure)

### What to Work On

#### If You're Building Platform (Now - Weeks 1-8)
Start with **Core Infrastructure** (Sprint 1):

```bash
cd src/psyai/core

# 1. Implement configuration management
# 2. Set up logging system
# 3. Create base exceptions
# 4. Build utility functions
# 5. Write tests

# See src/psyai/core/README.md for details
```

**Build Order:**
1. Core (Weeks 1-2) →
2. LangChain (Weeks 2-4) →
3. LangSmith (Weeks 4-5) →
4. Centaur (Weeks 5-6) →
5. Storage (Weeks 6-7) →
6. API (Weeks 7-8)

#### If You're Building Features (Weeks 9-12)
**Wait for platform to be complete!**

Once platform is ready, choose a feature:
- **Chat** - `src/psyai/features/chat/`
- **Evals** - `src/psyai/features/evals/`
- **Confidence** - `src/psyai/features/confidence/`
- **HITL** - `src/psyai/features/hitl/` (depends on Evals)

## For Project Managers

### Critical Path

```
Week 1-8:  Platform (BLOCKING - must be serial)
Week 8:    Platform Complete (MILESTONE)
Week 9-12: Features (parallel development possible)
Week 12:   Features Complete (MILESTONE)
Week 13-15: Integration Testing
Week 15:   Production Ready
```

### Team Allocation

**Minimum:**
- 2 Senior Engineers (Platform, Weeks 1-8)
- 4 Engineers (Features, Weeks 9-12)

**Optimal:**
- 2 Senior Engineers (Platform)
- 6 Engineers (Features, 1.5 per feature)
- 1 DevOps Engineer
- 1 QA Engineer

### Risk Factors

1. **Platform Delays** - Cascades to all features
   - Mitigation: 2-week buffer, clear interfaces early

2. **Centaur Model Access** - May not have API
   - Mitigation: Abstraction layer for model swapping

3. **Feature Dependencies** - HITL needs Evals
   - Mitigation: Stagger start dates

## For Contributors

### Contributing to Platform

Platform development is serial - coordinate with the platform team:

1. Check current sprint in ROADMAP.md
2. Look for open issues in that sprint
3. Follow platform coding standards
4. Ensure 80%+ test coverage
5. Document all public interfaces

### Contributing to Features

Feature development is parallel - pick a feature:

1. **Prerequisite:** Platform must be complete (Week 8+)
2. Choose a feature: chat, evals, hitl, or confidence
3. Read feature README: `src/psyai/features/{feature}/README.md`
4. Check feature development checklist
5. Coordinate with feature team lead

### Coding Standards

- **Python 3.11+** required
- **Type hints** everywhere (`mypy` enforced)
- **Tests** required (80%+ coverage)
- **Documentation** required (docstrings + README)
- **Code style:** Black, Ruff, isort (pre-commit hooks)

## Key Documents

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and component details |
| [ROADMAP.md](ROADMAP.md) | Build timeline and sprint plans |
| [README.md](README.md) | Project vision and goals |
| src/psyai/core/README.md | Core infrastructure guide |
| src/psyai/platform/README.md | Platform layer guide |
| src/psyai/features/README.md | Feature layer guide |

## Development Workflow

### 1. Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
black src/
ruff src/
mypy src/

# Run application
uvicorn psyai.platform.api.app:app --reload
```

### 2. Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=psyai --cov-report=html

# Run specific component
pytest tests/unit/core/
pytest tests/unit/platform/langchain_integration/
pytest tests/unit/features/chat/
```

### 3. Database Management

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### 4. Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Restart service
docker-compose restart api

# Stop all
docker-compose down
```

## FAQ

**Q: Can I start building features now?**
A: No, wait for platform to be complete (Week 8). You can help with platform development.

**Q: Which feature should I work on?**
A: After Week 8, choose based on interest. Chat and Confidence can start immediately. HITL requires Evals to be functional first.

**Q: What if Centaur model isn't accessible?**
A: We're building an abstraction layer. You can use a different decision prediction model.

**Q: How do features communicate?**
A: Through platform services only. No direct feature-to-feature imports.

**Q: Can features share code?**
A: Only through platform. Put shared logic in platform, not in features.

**Q: What about the Q1 2026 research study?**
A: Production deployment (Week 15) targets study preparation. All features must be complete and tested.

## Getting Help

- **Architecture Questions:** See ARCHITECTURE.md
- **Timeline Questions:** See ROADMAP.md
- **Implementation Questions:** See component READMEs
- **Issues:** Open GitHub issue
- **Urgent:** Contact project maintainers

## Next Steps

1. ✅ **You are here** - Repository structured
2. ⏭ **Next** - Sprint 1: Core Infrastructure (Weeks 1-2)
3. **Then** - Continue platform development (Weeks 2-8)
4. **Finally** - Parallel feature development (Weeks 9-12)

**Ready to contribute?** Start with the [Core Infrastructure README](src/psyai/core/README.md)!

---

*Last Updated: 2025-11-13*
