"""
Confidence scoring and decision alignment utilities.

This module provides high-level utilities for calculating confidence scores
and making decision alignment predictions using the Centaur model.
"""

from typing import Any, Dict, List, Optional

from psyai.core.config import get_settings
from psyai.core.exceptions import ValidationError
from psyai.core.logging import get_logger
from psyai.platform.centaur_integration.client import get_centaur_client

logger = get_logger(__name__)
settings = get_settings()


class ConfidenceScorer:
    """
    Confidence scorer for AI responses.

    This class provides methods to calculate confidence scores for AI-generated
    responses using the Centaur Foundation Model.

    Example:
        >>> scorer = ConfidenceScorer()
        >>> result = await scorer.score_response(
        ...     ai_response="Python is ideal for machine learning",
        ...     context="What's the best language for ML?"
        ... )
        >>> print(result.overall_score)  # 0.92
        >>> print(result.should_review)  # False
    """

    def __init__(
        self,
        review_threshold: Optional[float] = None,
        min_confidence: Optional[float] = None,
    ):
        """
        Initialize confidence scorer.

        Args:
            review_threshold: Threshold below which human review is recommended
            min_confidence: Minimum acceptable confidence score
        """
        self.review_threshold = review_threshold or settings.eval_failure_threshold or 0.7
        self.min_confidence = min_confidence or 0.5
        self.client = get_centaur_client()

        logger.info(
            "confidence_scorer_initialized",
            review_threshold=self.review_threshold,
            min_confidence=self.min_confidence,
        )

    async def score_response(
        self,
        ai_response: str,
        context: str,
        user_feedback: Optional[str] = None,
    ) -> "ConfidenceScore":
        """
        Score an AI response.

        Args:
            ai_response: The AI-generated response
            context: Context/prompt that led to the response
            user_feedback: Optional user feedback

        Returns:
            ConfidenceScore object

        Example:
            >>> score = await scorer.score_response(
            ...     ai_response="The capital of France is Paris",
            ...     context="What is the capital of France?"
            ... )
            >>> print(score.overall_score)  # 0.98
        """
        logger.info("scoring_response", response_length=len(ai_response))

        # Get confidence from Centaur
        result = await self.client.calculate_confidence_score(
            ai_response=ai_response,
            context=context,
            user_feedback=user_feedback,
        )

        # Create score object
        score = ConfidenceScore(
            overall_score=result["confidence_score"],
            dimensions=result["dimensions"],
            explanation=result["explanation"],
            suggestions=result["suggestions"],
            review_threshold=self.review_threshold,
        )

        logger.info(
            "response_scored",
            overall_score=score.overall_score,
            should_review=score.should_review,
        )

        return score

    async def batch_score_responses(
        self,
        responses: List[Dict[str, str]],
    ) -> List["ConfidenceScore"]:
        """
        Score multiple responses in batch.

        Args:
            responses: List of dicts with 'ai_response', 'context', 'user_feedback'

        Returns:
            List of ConfidenceScore objects

        Example:
            >>> responses = [
            ...     {"ai_response": "...", "context": "..."},
            ...     {"ai_response": "...", "context": "..."},
            ... ]
            >>> scores = await scorer.batch_score_responses(responses)
        """
        scores = []
        for response in responses:
            score = await self.score_response(
                ai_response=response["ai_response"],
                context=response["context"],
                user_feedback=response.get("user_feedback"),
            )
            scores.append(score)

        logger.info("batch_scoring_complete", num_responses=len(scores))
        return scores


class ConfidenceScore:
    """
    Confidence score result.

    Represents the confidence assessment for an AI response.

    Attributes:
        overall_score: Overall confidence (0.0 to 1.0)
        dimensions: Breakdown by dimension
        explanation: Explanation of the score
        suggestions: Improvement suggestions
        should_review: Whether human review is recommended
    """

    def __init__(
        self,
        overall_score: float,
        dimensions: Dict[str, float],
        explanation: str,
        suggestions: List[str],
        review_threshold: float = 0.7,
    ):
        """
        Initialize confidence score.

        Args:
            overall_score: Overall confidence (0.0 to 1.0)
            dimensions: Scores by dimension
            explanation: Explanation text
            suggestions: List of suggestions
            review_threshold: Threshold for human review
        """
        self.overall_score = max(0.0, min(1.0, overall_score))
        self.dimensions = dimensions
        self.explanation = explanation
        self.suggestions = suggestions
        self.review_threshold = review_threshold

    @property
    def should_review(self) -> bool:
        """Whether human review is recommended."""
        return self.overall_score < self.review_threshold

    @property
    def confidence_level(self) -> str:
        """Get confidence level as string."""
        if self.overall_score >= 0.9:
            return "very_high"
        elif self.overall_score >= 0.7:
            return "high"
        elif self.overall_score >= 0.5:
            return "medium"
        else:
            return "low"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "overall_score": self.overall_score,
            "confidence_level": self.confidence_level,
            "dimensions": self.dimensions,
            "explanation": self.explanation,
            "suggestions": self.suggestions,
            "should_review": self.should_review,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ConfidenceScore(score={self.overall_score:.2f}, "
            f"level={self.confidence_level}, "
            f"review={self.should_review})"
        )


class DecisionAligner:
    """
    Decision alignment predictor.

    This class helps predict which decisions align best with human preferences
    and cognitive patterns.

    Example:
        >>> aligner = DecisionAligner()
        >>> result = await aligner.predict_choice(
        ...     context="User needs a laptop",
        ...     options=["MacBook", "ThinkPad", "Surface"],
        ...     user_profile={"profession": "developer", "os_preference": "unix"}
        ... )
        >>> print(result.predicted_choice)  # "MacBook"
        >>> print(result.confidence)  # 0.88
    """

    def __init__(self, min_confidence: Optional[float] = None):
        """
        Initialize decision aligner.

        Args:
            min_confidence: Minimum confidence for returning predictions
        """
        self.min_confidence = min_confidence or 0.5
        self.client = get_centaur_client()

        logger.info("decision_aligner_initialized", min_confidence=self.min_confidence)

    async def predict_choice(
        self,
        context: str,
        options: List[str],
        user_profile: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "AlignmentPrediction":
        """
        Predict which option aligns best with human decision-making.

        Args:
            context: Decision context
            options: Available options
            user_profile: Optional user profile
            metadata: Optional metadata

        Returns:
            AlignmentPrediction object

        Raises:
            ValidationError: If options are invalid
        """
        if not options:
            raise ValidationError("At least one option must be provided")

        logger.info("predicting_alignment", num_options=len(options))

        # Get prediction from Centaur
        result = await self.client.predict_alignment(
            context=context,
            options=options,
            user_profile=user_profile,
            metadata=metadata,
        )

        # Create prediction object
        prediction = AlignmentPrediction(
            predicted_choice=result["predicted_choice"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            option_scores=result["option_scores"],
            min_confidence=self.min_confidence,
        )

        logger.info(
            "alignment_predicted",
            choice=prediction.predicted_choice,
            confidence=prediction.confidence,
            is_confident=prediction.is_confident,
        )

        return prediction

    async def rank_options(
        self,
        context: str,
        options: List[str],
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rank all options by alignment score.

        Args:
            context: Decision context
            options: Available options
            user_profile: Optional user profile

        Returns:
            List of options with scores, sorted by score (descending)

        Example:
            >>> ranked = await aligner.rank_options(
            ...     context="Choose a restaurant",
            ...     options=["Italian", "Chinese", "Mexican"]
            ... )
            >>> print(ranked[0])  # {"option": "Italian", "score": 0.92}
        """
        prediction = await self.predict_choice(
            context=context,
            options=options,
            user_profile=user_profile,
        )

        # Sort options by score
        ranked = [
            {"option": option, "score": prediction.option_scores.get(option, 0.0)}
            for option in options
        ]
        ranked.sort(key=lambda x: x["score"], reverse=True)

        logger.info("options_ranked", num_options=len(ranked))
        return ranked


class AlignmentPrediction:
    """
    Alignment prediction result.

    Represents a prediction of which option best aligns with human decision-making.

    Attributes:
        predicted_choice: The predicted option
        confidence: Confidence in prediction (0.0 to 1.0)
        reasoning: Explanation of prediction
        option_scores: Scores for all options
        is_confident: Whether confidence meets threshold
    """

    def __init__(
        self,
        predicted_choice: str,
        confidence: float,
        reasoning: str,
        option_scores: Dict[str, float],
        min_confidence: float = 0.5,
    ):
        """
        Initialize alignment prediction.

        Args:
            predicted_choice: Predicted option
            confidence: Confidence score
            reasoning: Reasoning text
            option_scores: Scores for all options
            min_confidence: Minimum confidence threshold
        """
        self.predicted_choice = predicted_choice
        self.confidence = max(0.0, min(1.0, confidence))
        self.reasoning = reasoning
        self.option_scores = option_scores
        self.min_confidence = min_confidence

    @property
    def is_confident(self) -> bool:
        """Whether the prediction meets minimum confidence."""
        return self.confidence >= self.min_confidence

    @property
    def confidence_level(self) -> str:
        """Get confidence level as string."""
        if self.confidence >= 0.9:
            return "very_high"
        elif self.confidence >= 0.7:
            return "high"
        elif self.confidence >= 0.5:
            return "medium"
        else:
            return "low"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "predicted_choice": self.predicted_choice,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level,
            "reasoning": self.reasoning,
            "option_scores": self.option_scores,
            "is_confident": self.is_confident,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"AlignmentPrediction(choice={self.predicted_choice}, "
            f"confidence={self.confidence:.2f}, "
            f"level={self.confidence_level})"
        )


# Utility functions

async def quick_confidence_check(
    ai_response: str,
    context: str,
    threshold: float = 0.7,
) -> bool:
    """
    Quick check if AI response meets confidence threshold.

    Args:
        ai_response: AI response to check
        context: Context of the response
        threshold: Confidence threshold

    Returns:
        True if confidence is above threshold

    Example:
        >>> is_confident = await quick_confidence_check(
        ...     ai_response="The answer is 42",
        ...     context="What is the meaning of life?"
        ... )
    """
    scorer = ConfidenceScorer(review_threshold=threshold)
    score = await scorer.score_response(ai_response, context)
    return not score.should_review


async def quick_alignment_prediction(
    context: str,
    options: List[str],
    user_profile: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Quick prediction of best-aligned option.

    Args:
        context: Decision context
        options: Available options
        user_profile: Optional user profile

    Returns:
        Predicted option

    Example:
        >>> choice = await quick_alignment_prediction(
        ...     context="Choose dessert",
        ...     options=["cake", "ice cream", "fruit"]
        ... )
    """
    aligner = DecisionAligner()
    prediction = await aligner.predict_choice(context, options, user_profile)
    return prediction.predicted_choice
