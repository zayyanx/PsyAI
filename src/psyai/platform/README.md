# Platform Layer

**Build Order:** 2nd-6th (Sprints 2-6, Weeks 2-8)
**Dependencies:** Core Infrastructure

## Overview

The platform layer provides foundational services that all features depend on. These components must be built serially as they have dependencies on each other.

## Platform Components

### 1. LangChain/LangGraph Integration
**Directory:** `langchain_integration/`
**Build Order:** 2nd (Weeks 2-4)
**Dependencies:** Core Infrastructure

Provides agentic workflow capabilities using LangChain and LangGraph.

**Components:**
- `chains/` - Reusable LangChain chains
- `agents/` - Agent base classes and tools
- `graphs/` - LangGraph state machines and workflows
- `rag/` - RAG implementation (vectors, embeddings, retrieval)

### 2. LangSmith Integration
**Directory:** `langsmith_integration/`
**Build Order:** 3rd (Weeks 4-5)
**Dependencies:** Core, LangChain Integration

Provides observability, tracing, and evaluation capabilities.

**Components:**
- `client.py` - LangSmith client wrapper
- `evaluators/` - Custom evaluators and metrics
- `tracers/` - Tracing decorators and utilities

### 3. Centaur Model Integration
**Directory:** `centaur_integration/`
**Build Order:** 4th (Weeks 5-6)
**Dependencies:** Core, LangChain Integration

Integrates with Centaur Foundation Model for decision alignment prediction.

**Components:**
- `client.py` - Centaur API client
- `prompts/` - Prompt templates for decision alignment
- `scoring.py` - Confidence score calculation

### 4. Storage Layer
**Directory:** `storage/`
**Build Order:** 5th (Weeks 6-7)
**Dependencies:** Core

Provides persistent data storage using PostgreSQL, Redis, and vector databases.

**Components:**
- `models/` - SQLAlchemy models
- `repositories/` - Repository pattern implementations
- `migrations/` - Alembic migration scripts

### 5. API Framework
**Directory:** `api/`
**Build Order:** 6th (Weeks 7-8)
**Dependencies:** All other platform components

Provides unified REST and WebSocket API layer for all features.

**Components:**
- `app.py` - FastAPI application setup
- `middleware/` - Authentication, CORS, rate limiting
- `schemas/` - Pydantic request/response models

## Build Strategy

The platform components must be built in order:

```
Core → LangChain → LangSmith → Centaur → Storage → API
  1        2          3          4         5        6
```

Each component builds on the previous ones and provides interfaces for the next.

## Testing

```bash
# Test all platform components
pytest tests/unit/platform/
pytest tests/integration/platform/

# Test specific platform component
pytest tests/unit/platform/langchain_integration/
```

## Documentation

Each platform component has detailed documentation in `docs/platform/`:
- `core.md`
- `langchain.md`
- `langsmith.md`
- `centaur.md`
- `storage.md`
- `api.md`

## Usage by Features

Features consume platform services through well-defined interfaces:

```python
# Example: Chat feature using platform services
from psyai.platform.langchain_integration import create_chat_chain
from psyai.platform.langsmith_integration import trace
from psyai.platform.storage import ChatRepository

@trace(name="chat_handler")
async def handle_chat(message: str, session_id: str):
    # Use LangChain for AI response
    chain = create_chat_chain()
    response = await chain.arun(message)

    # Store in database
    chat_repo = ChatRepository()
    await chat_repo.save_message(session_id, message, response)

    return response
```

## Interface Contracts

Platform components expose clear interfaces that features depend on:

- **LangChain:** Chain builders, agent factories, RAG pipelines
- **LangSmith:** Tracing decorators, evaluator base classes
- **Centaur:** Score calculation, confidence prediction
- **Storage:** Repository interfaces, model schemas
- **API:** Route decorators, auth middleware, WebSocket handlers

These interfaces should be defined early (Week 2-3) to enable feature planning.
