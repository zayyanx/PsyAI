# Core Infrastructure

**Build Order:** 1st (Sprint 1, Weeks 1-2)
**Dependencies:** None

## Overview

The core infrastructure provides foundational components used across all platform and feature modules.

## Components

### Configuration (`config.py`)
- Environment variable management
- Settings validation with Pydantic
- Application-wide configuration
- Feature flags

### Logging (`logging.py`)
- Structured logging with structlog
- Log levels and formatters
- Request/response logging
- Performance tracking

### Exceptions (`exceptions.py`)
- Base exception classes
- Domain-specific exceptions
- Error codes and messages
- Exception handlers

### Utils (`utils/`)
- Common utility functions
- Data validation helpers
- Type converters
- Retry logic
- Rate limiting utilities

## Usage

```python
from psyai.core.config import settings
from psyai.core.logging import get_logger
from psyai.core.exceptions import PsyAIException

logger = get_logger(__name__)

# Access configuration
api_key = settings.OPENAI_API_KEY
debug_mode = settings.APP_DEBUG

# Structured logging
logger.info("processing_request", user_id=123, action="chat")

# Raise exceptions
if not valid:
    raise PsyAIException("Invalid input", code="INVALID_INPUT")
```

## Development Checklist

- [ ] Set up project structure with `pyproject.toml`
- [ ] Implement configuration management
- [ ] Create logging system with structured logging
- [ ] Define base exception classes
- [ ] Create utility functions
- [ ] Set up testing framework (pytest)
- [ ] Configure CI/CD pipeline
- [ ] Write documentation
- [ ] Achieve 80%+ test coverage

## Testing

```bash
pytest tests/unit/core/
```

## Documentation

See `docs/platform/core.md` for detailed documentation.
