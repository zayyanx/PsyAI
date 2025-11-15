"""
Centaur Foundation Model integration for PsyAI.

This module provides integration with the Centaur Foundation Model for
decision alignment prediction and confidence scoring.

The Centaur model specializes in understanding human cognitive patterns and
decision-making processes, enabling AI systems to better align with human
preferences and predict confidence levels.

Example:
    >>> from psyai.platform.centaur_integration import (
    ...     get_centaur_client,
    ...     ConfidenceScorer,
    ...     DecisionAligner,
    ... )
    >>>
    >>> # Score AI response confidence
    >>> scorer = ConfidenceScorer()
    >>> result = await scorer.score_response(
    ...     ai_response="Python is great for ML",
    ...     context="What's the best language for ML?"
    ... )
    >>> print(result.overall_score)  # 0.92
    >>>
    >>> # Predict aligned decision
    >>> aligner = DecisionAligner()
    >>> prediction = await aligner.predict_choice(
    ...     context="User needs a laptop",
    ...     options=["MacBook", "ThinkPad", "Surface"],
    ...     user_profile={"profession": "developer"}
    ... )
    >>> print(prediction.predicted_choice)  # "MacBook"
"""

# Client
from psyai.platform.centaur_integration.client import (
    CentaurClient,
    get_centaur_client,
)

# Scoring and alignment
from psyai.platform.centaur_integration.scoring import (
    AlignmentPrediction,
    ConfidenceScore,
    ConfidenceScorer,
    DecisionAligner,
    quick_alignment_prediction,
    quick_confidence_check,
)

# Prompts
from psyai.platform.centaur_integration.prompts import (
    ALIGNMENT_PROMPT_TEMPLATE,
    CONFIDENCE_PROMPT_TEMPLATE,
    create_alignment_prompt,
    create_confidence_prompt,
)

__all__ = [
    # Client
    "CentaurClient",
    "get_centaur_client",
    # Scoring
    "ConfidenceScorer",
    "ConfidenceScore",
    "DecisionAligner",
    "AlignmentPrediction",
    "quick_confidence_check",
    "quick_alignment_prediction",
    # Prompts
    "ALIGNMENT_PROMPT_TEMPLATE",
    "CONFIDENCE_PROMPT_TEMPLATE",
    "create_alignment_prompt",
    "create_confidence_prompt",
]
