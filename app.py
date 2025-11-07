import streamlit as st
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from transformers import pipeline
from datetime import datetime

# Initialize session state
if 'workflow_state' not in st.session_state:
    st.session_state.workflow_state = None
if 'decision_history' not in st.session_state:
    st.session_state.decision_history = []
if 'current_thread_id' not in st.session_state:
    st.session_state.current_thread_id = None
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if 'centaur_model' not in st.session_state:
    st.session_state.centaur_model = None
if 'workflow_app' not in st.session_state:
    st.session_state.workflow_app = None

# Define the state structure for the workflow
class DecisionState(TypedDict):
    scenario: str
    options: list[str]
    model_prediction: str
    confidence: float
    human_decision: str
    human_approved: bool
    timestamp: str
    status: str

# Load Centaur model (using a text classification model as proxy)
@st.cache_resource
def load_centaur_model():
    """Load the Centaur model from Hugging Face"""
    try:
        # Note: Using a zero-shot classification model as a proxy for decision-making
        # Replace with actual Centaur model if available
        model = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # Use CPU
        )
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# Node: Collect decision scenario
def collect_scenario(state: DecisionState) -> DecisionState:
    """Initial node to collect the scenario"""
    state["status"] = "scenario_collected"
    state["timestamp"] = datetime.now().isoformat()
    return state

# Node: Model prediction
def model_prediction(state: DecisionState) -> DecisionState:
    """Use Centaur model to predict the best decision"""
    model = st.session_state.centaur_model
    
    if model and state["options"]:
        try:
            result = model(
                state["scenario"],
                candidate_labels=state["options"],
                multi_label=False
            )
            
            # Get top prediction
            state["model_prediction"] = result["labels"][0]
            state["confidence"] = float(result["scores"][0])
            state["status"] = "prediction_made"
        except Exception as e:
            state["model_prediction"] = "Error in prediction"
            state["confidence"] = 0.0
            state["status"] = "prediction_error"
    else:
        state["model_prediction"] = "No model available"
        state["confidence"] = 0.0
        state["status"] = "prediction_error"
    
    return state

# Node: Human review (interrupt point)
def human_review(state: DecisionState) -> DecisionState:
    """Human-in-the-loop review node - requires human input"""
    state["status"] = "awaiting_human_review"
    return state

# Node: Finalize decision
def finalize_decision(state: DecisionState) -> DecisionState:
    """Finalize the decision based on human input"""
    if state.get("human_approved"):
        state["human_decision"] = state["model_prediction"]
    
    state["status"] = "completed"
    return state

# Build LangGraph workflow (cached)
@st.cache_resource
def build_workflow():
    """Build the human-in-the-loop workflow using LangGraph"""
    workflow = StateGraph(DecisionState)
    
    # Add nodes
    workflow.add_node("collect_scenario", collect_scenario)
    workflow.add_node("model_prediction", model_prediction)
    workflow.add_node("human_review", human_review)
    workflow.add_node("finalize_decision", finalize_decision)
    
    # Add edges
    workflow.add_edge("collect_scenario", "model_prediction")
    workflow.add_edge("model_prediction", "human_review")
    workflow.add_edge("human_review", "finalize_decision")
    workflow.add_edge("finalize_decision", END)
    
    # Set entry point
    workflow.set_entry_point("collect_scenario")
    
    # Compile with checkpointer for human-in-the-loop
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory, interrupt_after=["human_review"])
    
    return app

def get_workflow_app():
    """Get or create the workflow app, ensuring the same instance is reused"""
    if st.session_state.workflow_app is None:
        st.session_state.workflow_app = build_workflow()
    return st.session_state.workflow_app

# Streamlit UI
def main():
    st.title("🤖 Human-in-the-Loop Decision System")
    st.markdown("### Using Centaur Model with LangGraph")
    
    # Load model
    if not st.session_state.model_loaded:
        with st.spinner("Loading Centaur model..."):
            st.session_state.centaur_model = load_centaur_model()
            st.session_state.model_loaded = True
    
    if st.session_state.centaur_model is None:
        st.error("Failed to load the model. Please refresh the page.")
        return
    
    # Sidebar for workflow status
    with st.sidebar:
        st.header("📊 Workflow Status")
        if st.session_state.workflow_state:
            status = st.session_state.workflow_state.get("status", "Unknown")
            st.info(f"Current Status: **{status}**")
        else:
            st.info("No active workflow")
        
        st.markdown("---")
        st.header("📜 Decision History")
        if st.session_state.decision_history:
            for i, decision in enumerate(reversed(st.session_state.decision_history[-5:])):
                with st.expander(f"Decision {len(st.session_state.decision_history) - i}"):
                    st.write(f"**Scenario:** {decision['scenario'][:50]}...")
                    st.write(f"**Model:** {decision['model_prediction']}")
                    st.write(f"**Human:** {decision['human_decision']}")
                    st.write(f"**Approved:** {'✅' if decision['human_approved'] else '❌'}")
        else:
            st.write("No decisions yet")
    
    # Main content area
    tab1, tab2 = st.tabs(["🎯 New Decision", "🔄 Review Prediction"])
    
    with tab1:
        st.header("Submit a Decision Scenario")
        
        # Input form
        with st.form("decision_form"):
            scenario = st.text_area(
                "Describe the decision scenario:",
                placeholder="Example: Should we launch the new product in Q1 or Q2 based on market conditions?",
                height=100
            )
            
            st.write("**Decision Options:**")
            col1, col2 = st.columns(2)
            with col1:
                option1 = st.text_input("Option 1:", placeholder="Launch in Q1")
                option2 = st.text_input("Option 2:", placeholder="Launch in Q2")
            with col2:
                option3 = st.text_input("Option 3 (optional):", placeholder="Delay to Q3")
                option4 = st.text_input("Option 4 (optional):", placeholder="Cancel launch")
            
            submitted = st.form_submit_button("🚀 Get AI Prediction", use_container_width=True)
            
            if submitted:
                options = [opt for opt in [option1, option2, option3, option4] if opt.strip()]
                
                if not scenario.strip():
                    st.error("Please provide a scenario description")
                elif len(options) < 2:
                    st.error("Please provide at least 2 options")
                else:
                    try:
                        # Get workflow app
                        workflow_app = get_workflow_app()
                        
                        # Initialize state
                        initial_state = {
                            "scenario": scenario,
                            "options": options,
                            "model_prediction": "",
                            "confidence": 0.0,
                            "human_decision": "",
                            "human_approved": False,
                            "timestamp": "",
                            "status": "initialized"
                        }
                        
                        # Generate thread ID
                        thread_id = f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        st.session_state.current_thread_id = thread_id
                        config = {"configurable": {"thread_id": thread_id}}
                        
                        # Run workflow until interrupt
                        with st.spinner("AI is analyzing your scenario..."):
                            result = None
                            for event in workflow_app.stream(initial_state, config):
                                for node_name, node_state in event.items():
                                    result = node_state
                            
                            if result is None:
                                st.error("❌ Workflow did not produce any result. Please try again.")
                            else:
                                st.session_state.workflow_state = result
                                st.success("✅ AI prediction ready! Switch to 'Review Prediction' tab.")
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error during prediction: {str(e)}")
                        print(f"ERROR: Exception during workflow execution: {e}")
                        import traceback
                        traceback.print_exc()
    
    with tab2:
        st.header("Review AI Prediction")
        
        if st.session_state.workflow_state and st.session_state.workflow_state.get("status") == "awaiting_human_review":
            state = st.session_state.workflow_state
            
            # Display scenario
            st.markdown("### 📋 Scenario")
            st.info(state["scenario"])
            
            # Display options
            st.markdown("### 🎲 Available Options")
            for i, option in enumerate(state["options"], 1):
                st.write(f"{i}. {option}")
            
            # Display prediction
            st.markdown("### 🤖 AI Prediction")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.success(f"**Recommended Decision:** {state['model_prediction']}")
            with col2:
                confidence_pct = state['confidence'] * 100
                st.metric("Confidence", f"{confidence_pct:.1f}%")
            
            # Confidence bar
            st.progress(state['confidence'])
            
            st.markdown("---")
            
            # Human decision interface
            st.markdown("### 👤 Your Decision")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("✅ Approve AI Decision", use_container_width=True, type="primary"):
                    # Get workflow app
                    workflow_app = get_workflow_app()
                    config = {"configurable": {"thread_id": st.session_state.current_thread_id}}
                    
                    # Update state in checkpoint with approval
                    workflow_app.update_state(
                        config,
                        {"human_approved": True, "human_decision": state["model_prediction"]}
                    )
                    
                    # Resume workflow
                    result = None
                    for event in workflow_app.stream(None, config):
                        for node_name, node_state in event.items():
                            result = node_state
                    
                    # Save to history
                    st.session_state.decision_history.append(result)
                    st.session_state.workflow_state = None
                    
                    st.success("✅ Decision approved and recorded!")
                    st.rerun()
            
            with col2:
                override_decision = st.selectbox(
                    "Or choose different option:",
                    [""] + state["options"],
                    key="override_select"
                )
            
            with col3:
                if st.button("🔄 Override", use_container_width=True, disabled=not override_decision):
                    # Get workflow app
                    workflow_app = get_workflow_app()
                    config = {"configurable": {"thread_id": st.session_state.current_thread_id}}
                    
                    # Update state in checkpoint with override
                    workflow_app.update_state(
                        config,
                        {"human_approved": False, "human_decision": override_decision}
                    )
                    
                    # Resume workflow
                    result = None
                    for event in workflow_app.stream(None, config):
                        for node_name, node_state in event.items():
                            result = node_state
                    
                    # Save to history
                    st.session_state.decision_history.append(result)
                    st.session_state.workflow_state = None
                    
                    st.success("✅ Override decision recorded!")
                    st.rerun()
            
        elif st.session_state.workflow_state and st.session_state.workflow_state.get("status") == "completed":
            st.info("✅ Previous decision has been completed. Submit a new scenario in the 'New Decision' tab.")
        else:
            st.info("👈 No pending prediction. Submit a decision scenario in the 'New Decision' tab.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.9em;'>
        Human-in-the-Loop Decision System | Powered by LangGraph & Hugging Face
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
