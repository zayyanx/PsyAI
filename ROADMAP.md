# PsyAI Development Roadmap

## Overview

This roadmap outlines the build order for PsyAI, with clear dependencies and parallel work opportunities.

---

## Build Order Summary

```
SERIAL (Platform):    [1] → [2] → [3] → [4] → [5] → [6]
                                                      ↓
PARALLEL (Features):               [Chat] [Evals] [HITL] [Confidence]
```

---

## Phase 1: Platform Components (Serial - 8 weeks)

### Sprint 1: Core Infrastructure (Weeks 1-2)

**Goal:** Establish project foundation

**Tasks:**
- [ ] Set up project structure and package configuration
- [ ] Create `pyproject.toml` with dependencies
- [ ] Set up development environment (venv, pre-commit hooks)
- [ ] Implement logging system with structured logging
- [ ] Create configuration management (settings, env vars)
- [ ] Define base exceptions and error handling
- [ ] Set up testing framework (pytest, coverage)
- [ ] Create shared utilities and helpers
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Create `.gitignore` for Python project
- [ ] Write core infrastructure documentation

**Deliverables:**
- ✅ Runnable Python package
- ✅ Logging system
- ✅ Config management
- ✅ Testing framework
- ✅ CI/CD pipeline

**Dependencies:** None

**Team:** 1-2 Senior Engineers

---

### Sprint 2: LangChain/LangGraph Integration (Weeks 2-4)

**Goal:** Enable agentic workflow capabilities

**Tasks:**
- [ ] Install and configure LangChain dependencies
- [ ] Create LangChain client wrapper with error handling
- [ ] Implement base agent classes and tools
- [ ] Design LangGraph state management patterns
- [ ] Create reusable chain templates
- [ ] Implement RAG foundation:
  - [ ] Vector store abstraction
  - [ ] Embedding service
  - [ ] Document loader utilities
  - [ ] Retrieval pipeline
- [ ] Set up prompt management system
- [ ] Create memory management utilities
- [ ] Write comprehensive tests for all components
- [ ] Document integration patterns and usage

**Deliverables:**
- ✅ LangChain integration layer
- ✅ LangGraph workflow engine
- ✅ RAG foundation
- ✅ Agent base classes
- ✅ Documentation with examples

**Dependencies:** Core Infrastructure (Sprint 1)

**Team:** 1-2 Senior Engineers

---

### Sprint 3: LangSmith Integration (Weeks 4-5)

**Goal:** Enable monitoring, tracing, and evaluation

**Tasks:**
- [ ] Install and configure LangSmith SDK
- [ ] Create LangSmith client wrapper
- [ ] Implement tracing decorators for automatic instrumentation
- [ ] Create dataset management utilities
- [ ] Build base evaluation framework:
  - [ ] Evaluator base class
  - [ ] Common evaluators (accuracy, relevance, etc.)
  - [ ] Evaluation runner
  - [ ] Results aggregation
- [ ] Implement metrics collection and reporting
- [ ] Set up experiment tracking
- [ ] Create monitoring dashboards configuration
- [ ] Write tests for all evaluators
- [ ] Document evaluation patterns

**Deliverables:**
- ✅ LangSmith integration
- ✅ Tracing system
- ✅ Evaluation framework
- ✅ Metrics collection
- ✅ Documentation

**Dependencies:** Core Infrastructure, LangChain/LangGraph Integration

**Team:** 1-2 Senior Engineers

---

### Sprint 4: Centaur Model Integration (Weeks 5-6)

**Goal:** Enable decision alignment prediction

**Tasks:**
- [ ] Research Centaur Foundation Model API/access
- [ ] Create Centaur client wrapper
- [ ] Implement prompt engineering for decision alignment:
  - [ ] Prompt templates for different decision types
  - [ ] Context formatting utilities
  - [ ] Input validation
- [ ] Build confidence score calculation logic
- [ ] Create response parsing and validation
- [ ] Implement caching layer for predictions
- [ ] Add retry logic and error handling
- [ ] Create scoring thresholds configuration
- [ ] Write comprehensive tests with mock responses
- [ ] Document Centaur integration and usage

**Deliverables:**
- ✅ Centaur model client
- ✅ Prompt engineering system
- ✅ Confidence scoring
- ✅ Caching layer
- ✅ Documentation

**Dependencies:** Core Infrastructure, LangChain Integration

**Team:** 1-2 Senior Engineers

**Note:** If Centaur API is not accessible, create abstraction layer for easy swapping with alternative decision prediction models.

---

### Sprint 5: Storage Layer (Weeks 6-7)

**Goal:** Provide persistent data storage

**Tasks:**
- [ ] Set up database (PostgreSQL) with Docker
- [ ] Install SQLAlchemy and create base configuration
- [ ] Design database schema:
  - [ ] Chat sessions and messages
  - [ ] Evaluations and results
  - [ ] Reviews and decisions
  - [ ] Users and roles
  - [ ] Confidence scores
- [ ] Create SQLAlchemy models
- [ ] Implement repository pattern for each entity
- [ ] Set up Alembic for migrations
- [ ] Create initial migration scripts
- [ ] Implement Redis caching layer
- [ ] Set up vector database (Pinecone/Weaviate/Chroma)
- [ ] Create database seeding scripts for development
- [ ] Write tests for all repositories
- [ ] Document data models and storage patterns

**Deliverables:**
- ✅ Database setup and schema
- ✅ ORM models
- ✅ Repository layer
- ✅ Migration system
- ✅ Caching layer
- ✅ Vector database
- ✅ Documentation

**Dependencies:** Core Infrastructure

**Team:** 1-2 Senior Engineers

---

### Sprint 6: API Framework (Weeks 7-8)

**Goal:** Create unified API layer for features

**Tasks:**
- [ ] Set up FastAPI application
- [ ] Configure CORS, middleware, and security
- [ ] Implement authentication system (JWT)
- [ ] Create authorization/permissions framework
- [ ] Define base request/response schemas (Pydantic)
- [ ] Set up WebSocket support for real-time features
- [ ] Implement API versioning strategy
- [ ] Create rate limiting and quota system
- [ ] Set up API documentation (OpenAPI/Swagger)
- [ ] Implement health check endpoints
- [ ] Create error handling middleware
- [ ] Write API integration tests
- [ ] Document API patterns and standards

**Deliverables:**
- ✅ FastAPI application
- ✅ Authentication/authorization
- ✅ WebSocket support
- ✅ API documentation
- ✅ Rate limiting
- ✅ Integration tests

**Dependencies:** All previous platform components

**Team:** 1-2 Senior Engineers

---

## Phase 2: Feature Components (Parallel - 6 weeks)

**Prerequisites:** All platform components (Sprints 1-6) must be complete

### Track A: Chat Feature (Weeks 9-10)

**Team:** 1-2 Engineers

**Tasks:**
- [ ] Design chat service architecture
- [ ] Implement session management
- [ ] Build chat modes:
  - [ ] Talk to End-User (AI agent mode)
  - [ ] Talk to Expert (human expert mode)
  - [ ] Direct Passthrough (expert-to-end-user)
- [ ] Create message routing logic
- [ ] Implement WebSocket handlers for real-time chat
- [ ] Build chat history retrieval and context management
- [ ] Integrate with LangChain for AI responses
- [ ] Add evaluation triggers after AI responses
- [ ] Create REST and WebSocket endpoints
- [ ] Write unit and integration tests
- [ ] Document chat API and usage

**API Endpoints:**
```
POST   /v1/chat/end-user
POST   /v1/chat/expert
POST   /v1/chat/passthrough
GET    /v1/chat/history/{session_id}
WS     /v1/chat/stream
```

**Deliverables:**
- ✅ Chat service with 3 modes
- ✅ WebSocket real-time support
- ✅ Session management
- ✅ API endpoints
- ✅ Tests and documentation

---

### Track B: Evals Feature (Weeks 9-11)

**Team:** 1-2 Engineers

**Tasks:**
- [ ] Design evaluation service architecture
- [ ] Implement evaluation runners
- [ ] Create custom evaluators:
  - [ ] Response quality evaluator
  - [ ] Relevance evaluator
  - [ ] Safety evaluator
  - [ ] Custom domain-specific evaluators
- [ ] Build RAG pipeline for eval context:
  - [ ] Integration with platform RAG
  - [ ] Context retrieval for evaluations
  - [ ] Prompt enhancement with context
- [ ] Implement dataset management
- [ ] Create results aggregation and reporting
- [ ] Build integration with LangSmith
- [ ] Add automatic eval triggering from chat
- [ ] Create evaluation metrics dashboard
- [ ] Write comprehensive tests
- [ ] Document evaluation framework

**API Endpoints:**
```
POST   /v1/evals/run
GET    /v1/evals/results/{eval_id}
POST   /v1/evals/datasets
GET    /v1/evals/metrics
GET    /v1/evals/datasets/{dataset_id}
```

**Deliverables:**
- ✅ Evaluation service
- ✅ Custom evaluators
- ✅ RAG-enhanced evals
- ✅ Dataset management
- ✅ API endpoints
- ✅ Tests and documentation

---

### Track C: HITL Feature (Weeks 11-12)

**Team:** 1 Engineer

**Dependencies:** Evals feature must be functional

**Tasks:**
- [ ] Design review workflow
- [ ] Implement review queue management
- [ ] Create fail detection logic (integrate with Evals)
- [ ] Build notification system for reviewers:
  - [ ] Email notifications
  - [ ] In-app notifications
  - [ ] Webhook support
- [ ] Implement review actions (Approve, Reject, Modify)
- [ ] Create decision tracking and audit log
- [ ] Build feedback loop to improve models
- [ ] Implement reviewer assignment logic
- [ ] Create review dashboard backend
- [ ] Write tests for review workflow
- [ ] Document HITL patterns

**API Endpoints:**
```
GET    /v1/hitl/queue
POST   /v1/hitl/review/{item_id}
GET    /v1/hitl/history
POST   /v1/hitl/assign/{reviewer_id}
GET    /v1/hitl/stats
```

**Deliverables:**
- ✅ Review queue system
- ✅ Notification system
- ✅ Review workflow
- ✅ Audit logging
- ✅ API endpoints
- ✅ Tests and documentation

---

### Track D: Confidence Score Feature (Weeks 9-10)

**Team:** 1-2 Engineers

**Tasks:**
- [ ] Design confidence scoring service
- [ ] Build prompt generation from chat input:
  - [ ] Extract decision points
  - [ ] Format for Centaur model
  - [ ] Add context
- [ ] Implement RAG pipeline for decision context:
  - [ ] Retrieve relevant past decisions
  - [ ] Gather domain knowledge
  - [ ] Enhance prompts with context
- [ ] Create confidence score calculation
- [ ] Implement score interpretation logic
- [ ] Build threshold management and configuration
- [ ] Integrate with Evals as metric provider
- [ ] Create score history tracking
- [ ] Write comprehensive tests
- [ ] Document confidence scoring

**API Endpoints:**
```
POST   /v1/confidence/score
GET    /v1/confidence/history/{session_id}
POST   /v1/confidence/threshold
GET    /v1/confidence/stats
```

**Deliverables:**
- ✅ Confidence scoring service
- ✅ Prompt generation
- ✅ RAG-enhanced scoring
- ✅ Integration with Evals
- ✅ API endpoints
- ✅ Tests and documentation

---

## Phase 3: Integration & Testing (Weeks 13-15)

**Goal:** Ensure all components work together seamlessly

**Team:** All engineers

**Tasks:**
- [ ] End-to-end workflow testing:
  - [ ] User chat → AI response → Eval → Confidence score
  - [ ] Failed eval → HITL review → Feedback loop
  - [ ] Expert chat → Passthrough → End-user
- [ ] Performance testing and optimization
- [ ] Load testing and scalability analysis
- [ ] Security audit and penetration testing
- [ ] API documentation finalization
- [ ] User documentation and guides
- [ ] Deployment preparation:
  - [ ] Docker containerization
  - [ ] Kubernetes manifests
  - [ ] Environment configuration
  - [ ] Monitoring and alerting setup
- [ ] Bug fixes and polish
- [ ] Final code review and refactoring

**Deliverables:**
- ✅ Fully integrated system
- ✅ Performance optimization
- ✅ Complete documentation
- ✅ Deployment-ready application
- ✅ Q1 2026 research study preparation

---

## Timeline Summary

| Phase | Duration | Weeks | Type |
|-------|----------|-------|------|
| **Platform** | 8 weeks | 1-8 | Serial |
| Core Infrastructure | 2 weeks | 1-2 | Serial |
| LangChain/LangGraph | 2 weeks | 2-4 | Serial |
| LangSmith | 1 week | 4-5 | Serial |
| Centaur | 1 week | 5-6 | Serial |
| Storage | 1 week | 6-7 | Serial |
| API Framework | 1 week | 7-8 | Serial |
| **Features** | 4 weeks | 9-12 | Parallel |
| Chat | 2 weeks | 9-10 | Parallel |
| Evals | 3 weeks | 9-11 | Parallel |
| HITL | 2 weeks | 11-12 | Parallel (after Evals) |
| Confidence | 2 weeks | 9-10 | Parallel |
| **Integration** | 3 weeks | 13-15 | Combined |
| **Total** | **15 weeks** | | **~3.5 months** |

---

## Critical Path

```
Weeks 1-8:  Platform (Serial) - BLOCKING
Week 8:     Platform complete - MILESTONE
Weeks 9-12: Features (Parallel) - NON-BLOCKING
Week 12:    Features complete - MILESTONE
Weeks 13-15: Integration - BLOCKING
Week 15:    Production ready - MILESTONE
```

---

## Risk Mitigation

### Platform Risks:
1. **Centaur Model Access:** May not have API access
   - **Mitigation:** Create abstraction layer for model swapping

2. **LangChain Breaking Changes:** Ecosystem evolving rapidly
   - **Mitigation:** Pin specific versions, monitor updates

3. **Platform Delays:** Cascades to all features
   - **Mitigation:** 2-week buffer, clear interface contracts early

### Feature Risks:
1. **Feature Interdependencies:** HITL depends on Evals
   - **Mitigation:** Stagger start dates, mock interfaces

2. **RAG Performance:** May be slow/expensive
   - **Mitigation:** Implement caching, optimize queries

3. **WebSocket Stability:** Real-time chat challenges
   - **Mitigation:** Fallback to polling, comprehensive testing

---

## Success Criteria

### Platform Complete (Week 8):
- [ ] All 6 platform components functional
- [ ] 80%+ test coverage
- [ ] API documentation complete
- [ ] Demo application working

### Features Complete (Week 12):
- [ ] All 4 features functional
- [ ] Features integrated with platform
- [ ] 80%+ test coverage per feature
- [ ] API documentation complete

### Production Ready (Week 15):
- [ ] End-to-end workflows functional
- [ ] Performance meets targets (< 2s response time)
- [ ] Security audit passed
- [ ] Deployment automated
- [ ] Ready for Q1 2026 research study

---

## Resource Allocation

### Minimum Team:
- **2 Senior Engineers** (Platform, weeks 1-8)
- **4 Engineers** (Features, weeks 9-12)
- **All Engineers** (Integration, weeks 13-15)

### Optimal Team:
- **2 Senior Engineers** (Platform)
- **6 Engineers** (Features - 1.5 per feature)
- **1 DevOps Engineer** (Infrastructure, CI/CD)
- **1 QA Engineer** (Testing, quality)

---

## Next Steps

1. **Immediate:** Set up project structure (Sprint 1, Week 1)
2. **Week 1:** Begin core infrastructure development
3. **Week 2:** LangChain/LangGraph planning and setup
4. **Week 8:** Platform review and feature team formation
5. **Week 9:** Kickoff parallel feature development
6. **Week 13:** Integration sprint begins
7. **Week 15:** Production deployment
8. **Q1 2026:** Research study launch

---

## Notes

- All sprints include testing, documentation, and code review time
- Weekly demos recommended to track progress
- Platform interfaces should be defined early (Week 2-3) to enable parallel feature planning
- Consider creating mock platform components in Week 6-7 to allow feature teams to start prototyping
