# PsyAI Architecture

## Overview

PsyAI is structured into two main categories:
1. **Platform Components** - Core infrastructure that must be built serially (dependencies)
2. **Feature Components** - Independent features that can be built in parallel once platform is ready

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Feature Layer (Parallel)                 │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Chat       │   Evals      │   HITL       │ Confidence     │
│   Feature    │   Feature    │   Feature    │ Score Feature  │
└──────────────┴──────────────┴──────────────┴────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Platform Layer (Serial)                     │
├─────────────────────────────────────────────────────────────┤
│  1. Core Infrastructure (config, utils, logging)            │
│  2. LangChain/LangGraph Integration                         │
│  3. LangSmith Integration                                   │
│  4. Centaur Model Integration                               │
│  5. Storage Layer (database, cache)                         │
│  6. API Framework                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Platform Components (Build Serially)

### 1. Core Infrastructure
**Build Order:** 1st
**Dependencies:** None
**Purpose:** Foundation for all other components

**Components:**
- Project configuration (`pyproject.toml`, environment variables)
- Logging and monitoring setup
- Error handling and exceptions
- Shared utilities and helpers
- Base abstractions and interfaces
- Testing framework setup

**Location:** `src/psyai/core/`

---

### 2. LangChain/LangGraph Integration
**Build Order:** 2nd
**Dependencies:** Core Infrastructure
**Purpose:** Agentic workflow orchestration

**Components:**
- LangChain client wrapper and configuration
- LangGraph workflow definitions and state management
- Custom chains and prompts
- RAG implementation base (vector stores, embeddings)
- Agent base classes and tools
- Memory management

**Location:** `src/psyai/platform/langchain_integration/`

---

### 3. LangSmith Integration
**Build Order:** 3rd
**Dependencies:** Core Infrastructure, LangChain/LangGraph
**Purpose:** Observability, monitoring, and evaluation

**Components:**
- LangSmith client configuration
- Tracing and logging decorators
- Dataset management
- Base evaluation framework
- Metrics collection and reporting

**Location:** `src/psyai/platform/langsmith_integration/`

---

### 4. Centaur Model Integration
**Build Order:** 4th
**Dependencies:** Core Infrastructure, LangChain Integration
**Purpose:** Decision alignment prediction

**Components:**
- Centaur model client/API wrapper
- Prompt engineering for decision alignment
- Confidence score calculation
- Model response parsing
- Caching layer for predictions

**Location:** `src/psyai/platform/centaur_integration/`

---

### 5. Storage Layer
**Build Order:** 5th
**Dependencies:** Core Infrastructure
**Purpose:** Persistent data storage

**Components:**
- Database models and schemas (chats, evals, reviews, decisions)
- Repository pattern implementations
- Migration system
- Caching layer (Redis/in-memory)
- Vector store integration (for RAG)

**Location:** `src/psyai/platform/storage/`

---

### 6. API Framework
**Build Order:** 6th
**Dependencies:** All other platform components
**Purpose:** Unified API layer for features

**Components:**
- REST API framework (FastAPI)
- Authentication and authorization
- Request/response models
- WebSocket support (for real-time chat)
- API versioning
- Rate limiting and quotas

**Location:** `src/psyai/platform/api/`

---

## Feature Components (Build in Parallel)

Once the platform is ready, these features can be developed independently:

### Feature 1: Chat
**Dependencies:** Platform (all 6 components)
**Parallel Build:** Yes

**Sub-features:**
1. **Talk to End-User** - Standard chat interface with AI agent
2. **Talk to Expert** - Human expert consultation mode
3. **Direct Message Passthrough** - Expert-to-end-user direct communication

**Components:**
- Chat service and business logic
- Session management
- Message routing logic
- Chat history and context management
- WebSocket handlers for real-time communication

**Location:** `src/psyai/features/chat/`

**API Endpoints:**
- `POST /chat/end-user` - Chat with AI agent
- `POST /chat/expert` - Consult with expert
- `POST /chat/passthrough` - Direct expert messaging
- `GET /chat/history/{session_id}` - Retrieve chat history
- `WS /chat/stream` - WebSocket for real-time chat

---

### Feature 2: Evals
**Dependencies:** Platform (all 6 components)
**Parallel Build:** Yes

**Sub-features:**
1. **LangSmith Evals** - Automated evaluation system
2. **RAG with LangGraph** - Context-enhanced evaluations

**Components:**
- Evaluation service and runners
- Custom evaluators and metrics
- RAG pipeline for eval context
- Evaluation dataset management
- Results aggregation and reporting

**Location:** `src/psyai/features/evals/`

**API Endpoints:**
- `POST /evals/run` - Execute evaluation
- `GET /evals/results/{eval_id}` - Get evaluation results
- `POST /evals/datasets` - Create evaluation dataset
- `GET /evals/metrics` - Retrieve metrics

---

### Feature 3: Human-in-the-Loop (HITL)
**Dependencies:** Platform + Evals Feature
**Parallel Build:** Yes (after Evals)

**Sub-features:**
1. **Fail Detection** - Identify failed evals and route for review
2. **Review Workflow** - Approve, Reject, Modify actions

**Components:**
- Review queue management
- Notification system (for reviewers)
- Review interface backend
- Decision tracking and audit log
- Feedback loop to improve models

**Location:** `src/psyai/features/hitl/`

**API Endpoints:**
- `GET /hitl/queue` - Get pending reviews
- `POST /hitl/review/{item_id}` - Submit review (approve/reject/modify)
- `GET /hitl/history` - Review history and audit log
- `POST /hitl/assign/{reviewer_id}` - Assign review task

---

### Feature 4: Confidence Score
**Dependencies:** Platform (especially Centaur Integration)
**Parallel Build:** Yes

**Sub-features:**
1. **Prompt Generation** - Create Centaur prompts from chat input
2. **RAG Enhancement** - Use LangGraph RAG for context
3. **Score Calculation** - Return confidence as eval metric

**Components:**
- Prompt engineering service
- RAG pipeline for decision context
- Confidence score calculator
- Score interpretation and thresholds
- Integration with Evals feature

**Location:** `src/psyai/features/confidence/`

**API Endpoints:**
- `POST /confidence/score` - Calculate confidence score
- `GET /confidence/history/{session_id}` - Score history
- `POST /confidence/threshold` - Configure thresholds

---

## Directory Structure

```
PsyAI/
├── README.md
├── ARCHITECTURE.md (this file)
├── ROADMAP.md (build order and timeline)
├── pyproject.toml
├── .gitignore
├── .env.example
│
├── src/
│   └── psyai/
│       ├── __init__.py
│       │
│       ├── core/                          # Platform Layer 1
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── logging.py
│       │   ├── exceptions.py
│       │   └── utils/
│       │
│       ├── platform/                      # Platform Layers 2-6
│       │   ├── __init__.py
│       │   ├── langchain_integration/     # Layer 2
│       │   │   ├── __init__.py
│       │   │   ├── chains/
│       │   │   ├── agents/
│       │   │   ├── graphs/
│       │   │   └── rag/
│       │   │
│       │   ├── langsmith_integration/     # Layer 3
│       │   │   ├── __init__.py
│       │   │   ├── client.py
│       │   │   ├── evaluators/
│       │   │   └── tracers/
│       │   │
│       │   ├── centaur_integration/       # Layer 4
│       │   │   ├── __init__.py
│       │   │   ├── client.py
│       │   │   ├── prompts/
│       │   │   └── scoring.py
│       │   │
│       │   ├── storage/                   # Layer 5
│       │   │   ├── __init__.py
│       │   │   ├── models/
│       │   │   ├── repositories/
│       │   │   └── migrations/
│       │   │
│       │   └── api/                       # Layer 6
│       │       ├── __init__.py
│       │       ├── app.py
│       │       ├── middleware/
│       │       └── schemas/
│       │
│       └── features/                      # Feature Layer (Parallel)
│           ├── __init__.py
│           │
│           ├── chat/
│           │   ├── __init__.py
│           │   ├── service.py
│           │   ├── routes.py
│           │   ├── models.py
│           │   └── websocket.py
│           │
│           ├── evals/
│           │   ├── __init__.py
│           │   ├── service.py
│           │   ├── routes.py
│           │   ├── evaluators/
│           │   └── rag/
│           │
│           ├── hitl/
│           │   ├── __init__.py
│           │   ├── service.py
│           │   ├── routes.py
│           │   ├── queue.py
│           │   └── notifications.py
│           │
│           └── confidence/
│               ├── __init__.py
│               ├── service.py
│               ├── routes.py
│               ├── prompts/
│               └── rag/
│
├── tests/
│   ├── unit/
│   │   ├── core/
│   │   ├── platform/
│   │   └── features/
│   └── integration/
│       ├── platform/
│       └── features/
│
├── docs/
│   ├── platform/
│   │   ├── core.md
│   │   ├── langchain.md
│   │   ├── langsmith.md
│   │   ├── centaur.md
│   │   ├── storage.md
│   │   └── api.md
│   └── features/
│       ├── chat.md
│       ├── evals.md
│       ├── hitl.md
│       └── confidence.md
│
├── scripts/
│   ├── setup_dev.sh
│   └── run_migrations.py
│
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

---

## Build Strategy

### Phase 1: Platform (Serial - 6-8 weeks)
Build components 1-6 in order. Each component builds on the previous one.

**Week 1-2:** Core Infrastructure
**Week 2-3:** LangChain/LangGraph Integration
**Week 3-4:** LangSmith Integration
**Week 4-5:** Centaur Model Integration
**Week 5-6:** Storage Layer
**Week 6-8:** API Framework

### Phase 2: Features (Parallel - 4-6 weeks)
Once platform is complete, all features can be built simultaneously by different teams/developers.

**Parallel Tracks:**
- **Track A:** Chat Feature (2 weeks)
- **Track B:** Evals Feature (3 weeks)
- **Track C:** HITL Feature (2 weeks, depends on Evals)
- **Track D:** Confidence Score Feature (2 weeks)

### Phase 3: Integration & Testing (2-3 weeks)
- End-to-end testing
- Performance optimization
- Documentation
- Deployment preparation

---

## Team Allocation (Suggested)

### Platform Team (Serial)
- **1-2 Senior Engineers** - Build platform components sequentially
- Focus on stability, extensibility, and documentation

### Feature Teams (Parallel - after platform ready)
- **Team 1:** Chat Feature (1-2 engineers)
- **Team 2:** Evals Feature (1-2 engineers)
- **Team 3:** HITL Feature (1 engineer, starts after Evals)
- **Team 4:** Confidence Feature (1-2 engineers)

---

## Key Integration Points

### How Features Use Platform:

**Chat Feature:**
- Uses LangChain for AI agent conversations
- Uses LangGraph for multi-step chat workflows
- Uses Storage for chat history
- Uses API Framework for endpoints
- Triggers Evals after responses

**Evals Feature:**
- Uses LangSmith for evaluation execution
- Uses LangGraph RAG for context
- Uses Storage for eval results
- Triggers HITL when evals fail

**HITL Feature:**
- Listens to Evals failures
- Uses Storage for review queue
- Uses API for review interface
- Feeds back to Chat and Evals

**Confidence Feature:**
- Uses Centaur for decision alignment
- Uses LangGraph RAG for context
- Uses Storage for score history
- Provides scores to Evals as metrics

---

## Development Principles

1. **Platform First:** No feature development until platform is stable
2. **Interface Contracts:** Define clear APIs between platform and features
3. **Independent Features:** Features should not directly depend on each other
4. **Shared Platform:** All features use the same platform components
5. **Testing:** Each component has unit and integration tests
6. **Documentation:** Every component has comprehensive docs

---

## Technology Stack

**Core:**
- Python 3.11+
- FastAPI (API framework)
- SQLAlchemy (ORM)
- PostgreSQL (database)
- Redis (caching)

**LangChain Ecosystem:**
- LangChain
- LangGraph
- LangSmith

**AI/ML:**
- Centaur Foundation Model
- OpenAI API (or other LLMs)
- Vector databases (Pinecone/Weaviate/Chroma)

**DevOps:**
- Docker
- pytest
- pre-commit hooks
- GitHub Actions CI/CD
