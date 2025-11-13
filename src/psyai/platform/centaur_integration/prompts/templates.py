"""
Prompt templates for Centaur Foundation Model.

This module provides templates for crafting prompts that help the Centaur model
predict human decision alignment and confidence scores.
"""

from typing import Any, Dict, List, Optional

# Template for decision alignment prediction
ALIGNMENT_PROMPT_TEMPLATE = """
You are an expert in human cognition and decision-making. Predict which option
a human would most likely choose given the context and user profile.

Context:
{context}

Available Options:
{options_list}

User Profile:
{user_profile}

Consider:
1. Human cognitive biases and heuristics
2. User demographics and preferences
3. Context-specific factors
4. Common decision patterns

Provide:
1. The most likely choice
2. Confidence score (0.0 to 1.0)
3. Reasoning based on cognitive science
4. Scores for each option
"""

# Template for confidence scoring
CONFIDENCE_PROMPT_TEMPLATE = """
You are an expert in evaluating AI-generated responses from a human perspective.
Assess how likely a human would agree with or accept the given AI response.

Context/Prompt:
{context}

AI Response:
{ai_response}

User Feedback (if available):
{user_feedback}

Evaluate the response on these dimensions:
1. Accuracy: Is the information factually correct?
2. Relevance: Does it address the user's query?
3. Clarity: Is it easy to understand?
4. Completeness: Does it provide sufficient information?
5. Tone: Is it appropriate for the context?

Provide:
1. Overall confidence score (0.0 to 1.0)
2. Breakdown by dimension
3. Explanation of the score
4. Suggestions for improvement
"""


def create_alignment_prompt(
    context: str,
    options: List[str],
    user_profile: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a decision alignment prediction prompt.

    Args:
        context: Decision context or scenario
        options: List of available options
        user_profile: Optional user profile information

    Returns:
        Formatted prompt string

    Example:
        >>> prompt = create_alignment_prompt(
        ...     context="Choose a vacation destination",
        ...     options=["Beach", "Mountains", "City"],
        ...     user_profile={"age": 30, "interests": ["hiking", "nature"]}
        ... )
    """
    # Format options list
    options_list = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])

    # Format user profile
    if user_profile:
        profile_str = "\n".join([f"- {k}: {v}" for k, v in user_profile.items()])
    else:
        profile_str = "Not provided"

    # Fill template
    return ALIGNMENT_PROMPT_TEMPLATE.format(
        context=context,
        options_list=options_list,
        user_profile=profile_str,
    )


def create_confidence_prompt(
    ai_response: str,
    context: str,
    user_feedback: Optional[str] = None,
) -> str:
    """
    Create a confidence scoring prompt.

    Args:
        ai_response: The AI-generated response to evaluate
        context: Context/prompt that led to the response
        user_feedback: Optional user feedback on the response

    Returns:
        Formatted prompt string

    Example:
        >>> prompt = create_confidence_prompt(
        ...     ai_response="Python is great for data science",
        ...     context="What's the best language for ML?"
        ... )
    """
    feedback_str = user_feedback if user_feedback else "No feedback provided"

    return CONFIDENCE_PROMPT_TEMPLATE.format(
        context=context,
        ai_response=ai_response,
        user_feedback=feedback_str,
    )


# Additional specialized templates

HITL_REVIEW_PROMPT_TEMPLATE = """
You are helping evaluate whether an AI decision should be reviewed by a human expert.

AI Decision:
{ai_decision}

Context:
{context}

Decision Metadata:
{metadata}

Consider:
1. Decision complexity and risk
2. Potential impact on users
3. Uncertainty in the decision
4. Domain expertise required
5. Stakes involved

Determine:
1. Should this decision be reviewed by a human? (yes/no)
2. Urgency level (low/medium/high)
3. Recommended reviewer expertise
4. Key factors requiring human judgment
"""


def create_hitl_review_prompt(
    ai_decision: str,
    context: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a prompt for human-in-the-loop review decision.

    Args:
        ai_decision: The AI's decision
        context: Decision context
        metadata: Additional decision metadata

    Returns:
        Formatted prompt string
    """
    metadata_str = "None provided"
    if metadata:
        metadata_str = "\n".join([f"- {k}: {v}" for k, v in metadata.items()])

    return HITL_REVIEW_PROMPT_TEMPLATE.format(
        ai_decision=ai_decision,
        context=context,
        metadata=metadata_str,
    )


# Evaluation templates

EVAL_QUALITY_PROMPT_TEMPLATE = """
Evaluate the quality of this AI response for use in evaluation datasets.

Input:
{input_data}

Expected Output:
{expected_output}

Actual Output:
{actual_output}

Assess:
1. Correctness: Does it match expected output?
2. Quality: Is it well-formed and complete?
3. Edge Cases: Does it handle edge cases?
4. Robustness: Would it work for similar inputs?

Provide:
1. Quality score (0.0 to 1.0)
2. Issues found
3. Suggestions for improvement
4. Whether this should be included in the dataset
"""


def create_eval_quality_prompt(
    input_data: Dict[str, Any],
    expected_output: Dict[str, Any],
    actual_output: Dict[str, Any],
) -> str:
    """
    Create a prompt for evaluating response quality.

    Args:
        input_data: Input to the system
        expected_output: Expected response
        actual_output: Actual system response

    Returns:
        Formatted prompt string
    """
    return EVAL_QUALITY_PROMPT_TEMPLATE.format(
        input_data=str(input_data),
        expected_output=str(expected_output),
        actual_output=str(actual_output),
    )
