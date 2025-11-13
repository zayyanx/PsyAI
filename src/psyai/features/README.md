# Features Layer

**Build Order:** After Platform (Weeks 9-12)
**Dependencies:** All platform components (1-6)

## Overview

Features are independent, user-facing capabilities that can be built in parallel once the platform is complete. Each feature consumes platform services but does not directly depend on other features.

## Feature Components

### 1. Chat Feature
**Directory:** `chat/`
**Build Time:** 2 weeks (Weeks 9-10)
**Team:** 1-2 Engineers
**Parallel:** Yes

Provides three chat modes for end-user and expert interaction.

**Sub-features:**
- Talk to End-User (AI agent mode)
- Talk to Expert (human expert consultation)
- Direct Message Passthrough (expert-to-end-user)

**Components:**
- `service.py` - Chat business logic
- `routes.py` - REST and WebSocket endpoints
- `models.py` - Chat data models
- `websocket.py` - Real-time chat handlers

**API Endpoints:**
```
POST   /v1/chat/end-user
POST   /v1/chat/expert
POST   /v1/chat/passthrough
GET    /v1/chat/history/{session_id}
WS     /v1/chat/stream
```

---

### 2. Evals Feature
**Directory:** `evals/`
**Build Time:** 3 weeks (Weeks 9-11)
**Team:** 1-2 Engineers
**Parallel:** Yes

Provides automated evaluation using LangSmith with RAG-enhanced context.

**Sub-features:**
- LangSmith Evals integration
- RAG with LangGraph for contextual evaluations

**Components:**
- `service.py` - Evaluation service
- `routes.py` - Evaluation endpoints
- `evaluators/` - Custom evaluators
- `rag/` - RAG pipeline for eval context

**API Endpoints:**
```
POST   /v1/evals/run
GET    /v1/evals/results/{eval_id}
POST   /v1/evals/datasets
GET    /v1/evals/metrics
```

---

### 3. Human-in-the-Loop (HITL) Feature
**Directory:** `hitl/`
**Build Time:** 2 weeks (Weeks 11-12)
**Team:** 1 Engineer
**Parallel:** Yes (but starts after Evals is functional)
**Dependencies:** Evals feature must be working

Provides review workflow for failed evaluations.

**Sub-features:**
- Automatic fail detection from evals
- Review workflow (Approve, Reject, Modify)

**Components:**
- `service.py` - Review service
- `routes.py` - Review endpoints
- `queue.py` - Review queue management
- `notifications.py` - Notification system

**API Endpoints:**
```
GET    /v1/hitl/queue
POST   /v1/hitl/review/{item_id}
GET    /v1/hitl/history
POST   /v1/hitl/assign/{reviewer_id}
```

---

### 4. Confidence Score Feature
**Directory:** `confidence/`
**Build Time:** 2 weeks (Weeks 9-10)
**Team:** 1-2 Engineers
**Parallel:** Yes

Calculates confidence scores using Centaur model with RAG enhancement.

**Sub-features:**
- Prompt generation from chat input for Centaur
- RAG with LangGraph for decision context
- Confidence score calculation as evaluation metric

**Components:**
- `service.py` - Confidence scoring service
- `routes.py` - Confidence endpoints
- `prompts/` - Prompt templates
- `rag/` - RAG pipeline for context

**API Endpoints:**
```
POST   /v1/confidence/score
GET    /v1/confidence/history/{session_id}
POST   /v1/confidence/threshold
GET    /v1/confidence/stats
```

---

## Build Strategy

Once the platform is complete (Week 8), features can be built in parallel:

```
Week 9-10:  Chat + Confidence (parallel)
Week 9-11:  Evals (parallel)
Week 11-12: HITL (depends on Evals)
```

### Parallel Build Diagram

```
Platform Complete (Week 8)
         │
         ├─────────┬─────────┬─────────┐
         │         │         │         │
      Chat      Evals   Confidence   │
    (W 9-10)  (W 9-11)  (W 9-10)     │
                 │                    │
                 └────────> HITL ─────┘
                         (W 11-12)
```

## Feature Independence

Features are designed to be independent:

- **No direct imports** between features
- **Communicate via platform** services
- **Shared state** only through database
- **Event-driven** where needed (via platform event bus)

Example - Features should NOT do this:
```python
# ❌ BAD: Direct feature-to-feature import
from psyai.features.evals import run_evaluation
```

Example - Features should do this:
```python
# ✅ GOOD: Use platform service
from psyai.platform.langsmith_integration import evaluate
```

## Inter-Feature Communication

When features need to communicate:

1. **Database:** Write to shared storage, other feature reads
2. **Events:** Publish events via platform event bus
3. **API:** Call another feature's API endpoint

### Example: Chat → Evals Flow

```python
# In Chat feature
async def send_message(message: str):
    response = await ai_agent.respond(message)

    # Store in database via platform
    await chat_repo.save_message(message, response)

    # Trigger eval via platform event
    await event_bus.publish("chat.response", {
        "message_id": message.id,
        "response": response
    })

# In Evals feature (separate process/module)
@event_bus.subscribe("chat.response")
async def on_chat_response(event):
    # Run evaluation
    result = await evaluate(event["response"])

    if result.failed:
        # Trigger HITL via event
        await event_bus.publish("eval.failed", {
            "message_id": event["message_id"],
            "eval_result": result
        })
```

## Testing

```bash
# Test all features
pytest tests/unit/features/
pytest tests/integration/features/

# Test specific feature
pytest tests/unit/features/chat/
pytest tests/unit/features/evals/
pytest tests/unit/features/hitl/
pytest tests/unit/features/confidence/
```

## Documentation

Each feature has detailed documentation in `docs/features/`:
- `chat.md`
- `evals.md`
- `hitl.md`
- `confidence.md`

## Development Workflow

### Step 1: Platform Complete (Prerequisite)
Before starting feature development, ensure all platform components are complete and tested.

### Step 2: Feature Kickoff
Each feature team should:
1. Review platform interfaces
2. Design feature architecture
3. Define API contracts
4. Create mock data for testing
5. Set up feature-specific tests

### Step 3: Parallel Development
- Teams work independently
- Weekly syncs to share progress
- Integration points defined early

### Step 4: Feature Integration
Once features are complete:
1. End-to-end workflow testing
2. Performance testing
3. Integration bug fixes
4. Documentation updates

## Success Criteria

Each feature is considered complete when:

- [ ] All API endpoints implemented and tested
- [ ] 80%+ test coverage
- [ ] Integration with platform services working
- [ ] Documentation complete
- [ ] Code review passed
- [ ] Deployed to staging environment

## Team Coordination

### Recommended Team Structure

**Week 8 (Planning):**
- All feature teams meet
- Review platform interfaces
- Discuss integration points
- Agree on API contracts

**Weeks 9-12 (Development):**
- Daily standups within feature teams
- Weekly cross-team syncs
- Shared Slack channel for questions
- Platform team available for support

**Week 13+ (Integration):**
- All teams collaborate
- End-to-end testing
- Bug fixes and polish
