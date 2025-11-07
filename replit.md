# Overview

This is a human-in-the-loop decision-making application built with Streamlit and LangGraph. The system implements a "Centaur" approach where AI models provide predictions and recommendations, but humans retain final decision-making authority. The application uses a state machine architecture to manage decision workflows, capturing scenarios, model predictions, confidence scores, and human approvals in a structured manner.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit for web UI and user interaction (port 5000)
- **State Management**: Streamlit's built-in session state for persisting workflow data, decision history, thread IDs, and model instances across reruns
- **Component Structure**: Single-file application (app.py) with stateful components for managing decision workflows
- **UI Tabs**: "New Decision" for submitting scenarios, "Review Prediction" for human-in-the-loop review and decision approval/override

## Backend Architecture
- **Workflow Engine**: LangGraph StateGraph for orchestrating decision-making workflows
- **State Machine Pattern**: TypedDict-based state structure (DecisionState) tracking scenarios, options, predictions, confidence, human decisions, approval status, and timestamps
- **Checkpointing**: MemorySaver for workflow state persistence, enabling workflow resumption and historical tracking across different threads
- **Thread Management**: Thread-based workflow instances for handling multiple concurrent decision processes
- **Workflow Caching**: @st.cache_resource decorator for get_workflow_app() ensures single workflow instance with persistent MemorySaver across all operations

## ML/AI Components
- **Model Architecture**: Hugging Face Transformers pipeline for zero-shot classification
- **Current Implementation**: Facebook BART-large-MNLI model (1.63GB) as a proxy for decision prediction
- **Inference**: CPU-based inference (device=-1 configuration)
- **Model Caching**: Streamlit's @st.cache_resource decorator on load_centaur_model() to avoid reloading models on each rerun
- **Design Pattern**: The application is designed to support swapping in a custom "Centaur" model when available

## Data Structure
- **Decision State Schema**:
  - scenario: Text description of the decision context
  - options: List of available choices (2-4 options)
  - model_prediction: AI-recommended option
  - confidence: Confidence score for prediction (0-1)
  - human_decision: Final human choice
  - human_approved: Boolean approval flag
  - timestamp: Decision timestamp (ISO format)
  - status: Current workflow status (initialized → scenario_collected → prediction_made → awaiting_human_review → completed)

**Rationale**: TypedDict provides type safety while maintaining flexibility for state machine transitions. The schema balances AI assistance with human oversight.

## Key Architectural Decisions

### Human-in-the-Loop Design
**Problem**: Need to balance AI automation with human judgment for critical decisions
**Solution**: Centaur architecture where AI provides recommendations but humans make final decisions
**Rationale**: Ensures accountability and allows humans to override AI when context or nuance requires human judgment. LangGraph interrupt_after feature pauses workflow after prediction for human review.

### State Machine Workflow  
**Problem**: Complex decision workflows with multiple steps and potential branches
**Solution**: LangGraph StateGraph with typed state management and interrupt points
**Rationale**: Provides clear workflow definition, state transitions, and debugging capabilities. Memory checkpointing enables workflow resumption and audit trails. The workflow uses interrupt_after=["human_review"] to pause execution after the human_review node sets status to "awaiting_human_review".

### Workflow Instance Persistence
**Problem**: Each button click in Streamlit rebuilds the graph, losing checkpoint context
**Solution**: get_workflow_app() function that caches the compiled workflow in st.session_state.workflow_app
**Rationale**: Ensures the same LangGraph instance with the same MemorySaver handles both initial execution and resume operations. Human inputs are persisted via update_state() before calling stream(None, config) to continue the workflow.

### Zero-Shot Classification Approach
**Problem**: Need flexible decision-making across varied scenarios without extensive training data
**Solution**: Zero-shot classification model (BART-large-MNLI) that can handle arbitrary decision options
**Rationale**: Allows the system to work with new decision scenarios without retraining, though may be replaced with domain-specific models as they become available. The model takes a scenario and candidate labels (options) and returns predictions with confidence scores.

## Workflow Execution Flow
1. User submits scenario with 2-4 decision options
2. Workflow executes: collect_scenario → model_prediction → human_review (interrupt)
3. Status changes through states and stops at "awaiting_human_review"
4. UI displays prediction with confidence score in Review Prediction tab
5. Human approves (uses AI decision) or overrides (selects different option)
6. update_state() persists human choice into checkpoint
7. Workflow resumes: finalize_decision → END
8. Completed decision added to decision_history in session state

# External Dependencies

## Third-Party Libraries
- **Streamlit**: Web application framework for building interactive data apps
- **LangGraph**: Workflow orchestration and state management library with checkpoint support
- **LangChain/LangChain-Core**: Supporting libraries for LangGraph functionality
- **Transformers (Hugging Face)**: ML model inference pipeline
- **PyTorch**: ML backend for model inference (CPU-only version)
- **Pandas**: Data handling for decision history
- **Python typing**: For type hints and TypedDict state definitions

## ML Models
- **facebook/bart-large-mnli**: Zero-shot classification model from Hugging Face Model Hub (1.63GB)
  - Purpose: Proxy model for decision prediction using zero-shot classification
  - Deployment: Downloaded on first run from Hugging Face Hub and cached locally
  - Inference: CPU-based (device=-1 parameter)
  - First load time: ~20-30 seconds to download and initialize

## Package Management
- Uses uv for Python package management
- Python version constrained to >=3.11,<3.12 to ensure dependency compatibility
- Special pytorch-cpu index configuration for CPU-only PyTorch installation

## Future Integration Points
- Custom Centaur model (currently using BART as placeholder)
- Persistent database for decision history storage (currently in-memory session state)
- External APIs for scenario data ingestion (not currently implemented)
- User authentication and multi-user support
- Analytics and model performance tracking
