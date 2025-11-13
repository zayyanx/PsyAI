# Chat Feature

**Build Time:** 2 weeks (Weeks 9-10)
**Team Size:** 1-2 Engineers
**Parallel Development:** Yes

## Overview

The Chat feature provides three distinct modes of interaction:
1. **Talk to End-User** - AI agent responds to end-user queries
2. **Talk to Expert** - Human expert consultation mode
3. **Direct Message Passthrough** - Expert communicates directly with end-user

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ├─── REST API ──────┐
       │                   │
       └─── WebSocket ─────┤
                           │
                    ┌──────▼──────┐
                    │ Chat Router │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼───┐   ┌───▼────┐   ┌──▼─────┐
         │  AI    │   │ Expert │   │ Direct │
         │  Mode  │   │  Mode  │   │  Pass  │
         └────┬───┘   └───┬────┘   └──┬─────┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │Chat Service │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼───┐   ┌───▼────┐   ┌──▼─────┐
         │LangChain   │ Storage│   │ Evals  │
         │Platform │   │Platform│   │Platform│
         └─────────┘   └────────┘   └────────┘
```

## Components

### `service.py` - Chat Service
Core business logic for chat operations.

**Key Classes:**
- `ChatService` - Main service class
- `SessionManager` - Manages chat sessions
- `MessageRouter` - Routes messages to appropriate handler

**Key Methods:**
```python
class ChatService:
    async def send_message_to_ai(
        self,
        session_id: str,
        message: str,
        user_id: str
    ) -> ChatResponse

    async def send_message_to_expert(
        self,
        session_id: str,
        message: str,
        user_id: str
    ) -> ChatResponse

    async def expert_passthrough(
        self,
        session_id: str,
        message: str,
        expert_id: str
    ) -> ChatResponse

    async def get_chat_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ChatMessage]
```

### `routes.py` - API Routes
REST and WebSocket endpoints.

**REST Endpoints:**
```python
@router.post("/end-user")
async def chat_with_ai(
    request: ChatRequest,
    user: User = Depends(get_current_user)
) -> ChatResponse

@router.post("/expert")
async def chat_with_expert(
    request: ChatRequest,
    user: User = Depends(get_current_user)
) -> ChatResponse

@router.post("/passthrough")
async def expert_passthrough_message(
    request: PassthroughRequest,
    expert: User = Depends(require_expert_role)
) -> ChatResponse

@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    limit: int = 50,
    user: User = Depends(get_current_user)
) -> ChatHistoryResponse
```

### `websocket.py` - WebSocket Handlers
Real-time bidirectional communication.

**WebSocket Endpoint:**
```python
@router.websocket("/stream")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...)
):
    # Authenticate
    user = await authenticate_websocket(token)

    # Accept connection
    await websocket.accept()

    # Handle messages
    async for message in websocket.iter_json():
        # Process message
        response = await chat_service.handle_message(message, user)

        # Send response
        await websocket.send_json(response)
```

### `models.py` - Data Models
Pydantic models for requests/responses.

**Key Models:**
```python
class ChatRequest(BaseModel):
    session_id: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message_id: str
    session_id: str
    content: str
    role: Literal["ai", "expert", "user"]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    id: str
    session_id: str
    content: str
    role: str
    timestamp: datetime
    user_id: Optional[str]
    expert_id: Optional[str]

class PassthroughRequest(BaseModel):
    session_id: str
    message: str
    target_user_id: str
```

## Implementation Details

### Mode 1: Talk to End-User (AI Agent)

**Flow:**
1. User sends message via REST or WebSocket
2. Message routed to AI handler
3. LangChain agent generates response
4. Response saved to database
5. Evaluation triggered (async)
6. Response returned to user

**Implementation:**
```python
async def send_message_to_ai(
    session_id: str,
    message: str,
    user_id: str
) -> ChatResponse:
    # Get session context
    session = await session_manager.get_or_create(session_id, user_id)

    # Get chat history for context
    history = await self.get_recent_history(session_id, limit=10)

    # Create LangChain chain with history
    chain = create_conversational_chain(history)

    # Generate response
    ai_response = await chain.arun(message)

    # Save messages
    await chat_repo.save_message(session_id, message, "user", user_id)
    message_id = await chat_repo.save_message(
        session_id, ai_response, "ai", None
    )

    # Trigger evaluation (fire and forget)
    asyncio.create_task(
        trigger_evaluation(message_id, message, ai_response)
    )

    return ChatResponse(
        message_id=message_id,
        session_id=session_id,
        content=ai_response,
        role="ai",
        timestamp=datetime.utcnow()
    )
```

### Mode 2: Talk to Expert

**Flow:**
1. User requests expert consultation
2. Expert notified (webhook/email)
3. Expert joins session
4. Messages exchanged in real-time
5. Session logged for analysis

**Implementation:**
```python
async def send_message_to_expert(
    session_id: str,
    message: str,
    user_id: str
) -> ChatResponse:
    # Get or assign expert
    expert = await expert_service.assign_expert(session_id)

    # Notify expert
    await notification_service.notify_expert(
        expert.id,
        session_id,
        message
    )

    # Save message
    message_id = await chat_repo.save_message(
        session_id, message, "user", user_id
    )

    # Update session status
    await session_manager.set_mode(session_id, "expert")

    return ChatResponse(
        message_id=message_id,
        session_id=session_id,
        content="Expert notified. You will receive a response shortly.",
        role="system",
        timestamp=datetime.utcnow()
    )
```

### Mode 3: Direct Passthrough

**Flow:**
1. Expert sends message directly to end-user
2. Message bypasses AI agent
3. End-user receives message
4. Optional: AI observes for context

**Implementation:**
```python
async def expert_passthrough(
    session_id: str,
    message: str,
    expert_id: str,
    target_user_id: str
) -> ChatResponse:
    # Verify expert has access to session
    await authorize_expert_access(expert_id, session_id)

    # Save message
    message_id = await chat_repo.save_message(
        session_id, message, "expert", expert_id
    )

    # Send to user via WebSocket if connected
    await websocket_manager.send_to_user(
        target_user_id,
        {
            "type": "expert_message",
            "message_id": message_id,
            "content": message,
            "session_id": session_id
        }
    )

    return ChatResponse(
        message_id=message_id,
        session_id=session_id,
        content=message,
        role="expert",
        timestamp=datetime.utcnow()
    )
```

## Platform Integration

### LangChain Integration
```python
from psyai.platform.langchain_integration import (
    create_conversational_chain,
    create_chat_memory
)

# Create chain with memory
memory = create_chat_memory(session_id)
chain = create_conversational_chain(memory=memory)
response = await chain.arun(message)
```

### Storage Integration
```python
from psyai.platform.storage import ChatRepository

chat_repo = ChatRepository()
await chat_repo.save_message(session_id, message, role, user_id)
history = await chat_repo.get_history(session_id, limit=50)
```

### Evaluation Integration
```python
from psyai.platform.langsmith_integration import evaluate

async def trigger_evaluation(message_id, input_msg, output_msg):
    result = await evaluate(
        input=input_msg,
        output=output_msg,
        evaluators=["relevance", "safety", "quality"]
    )

    if result.failed:
        # Trigger HITL via event
        await event_bus.publish("eval.failed", {
            "message_id": message_id,
            "eval_result": result
        })
```

## Testing

### Unit Tests
```bash
pytest tests/unit/features/chat/test_service.py
pytest tests/unit/features/chat/test_routes.py
pytest tests/unit/features/chat/test_websocket.py
```

### Integration Tests
```bash
pytest tests/integration/features/chat/
```

### Example Test
```python
@pytest.mark.asyncio
async def test_chat_with_ai():
    # Setup
    service = ChatService()
    session_id = "test-session"
    message = "Hello, AI!"

    # Execute
    response = await service.send_message_to_ai(
        session_id, message, "user-123"
    )

    # Assert
    assert response.role == "ai"
    assert len(response.content) > 0
    assert response.session_id == session_id
```

## API Examples

### REST API - Chat with AI
```bash
curl -X POST http://localhost:8000/v1/chat/end-user \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "message": "What is PsyAI?"
  }'
```

### WebSocket - Real-time Chat
```javascript
const ws = new WebSocket('ws://localhost:8000/v1/chat/stream?token=YOUR_TOKEN');

ws.onopen = () => {
  ws.send(JSON.stringify({
    session_id: 'session-123',
    message: 'Hello!'
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('AI:', response.content);
};
```

## Development Checklist

- [ ] Implement ChatService with three modes
- [ ] Create REST API endpoints
- [ ] Implement WebSocket handlers
- [ ] Integrate with LangChain platform
- [ ] Integrate with Storage platform
- [ ] Add evaluation triggers
- [ ] Implement session management
- [ ] Add authentication/authorization
- [ ] Write unit tests (80%+ coverage)
- [ ] Write integration tests
- [ ] Document API with OpenAPI
- [ ] Load test WebSocket connections
- [ ] Security audit

## Performance Targets

- **Response Time:** < 2 seconds for AI responses
- **WebSocket Latency:** < 100ms
- **Concurrent Connections:** > 1000 WebSocket connections
- **Throughput:** > 100 messages/second

## Security Considerations

- Validate all user inputs
- Rate limit per user/session
- Sanitize messages for XSS
- Encrypt WebSocket connections (WSS)
- Implement proper authentication
- Log all expert access for audit
