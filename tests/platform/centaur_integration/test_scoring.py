"""Tests for Centaur scoring utilities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from psyai.core.exceptions import ValidationError
from psyai.platform.centaur_integration.scoring import (
    AlignmentPrediction,
    ConfidenceScore,
    ConfidenceScorer,
    DecisionAligner,
    quick_alignment_prediction,
    quick_confidence_check,
)


@pytest.fixture
def mock_centaur_client():
    """Mock Centaur client."""
    with patch("psyai.platform.centaur_integration.scoring.get_centaur_client") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_settings():
    """Mock settings."""
    with patch("psyai.platform.centaur_integration.scoring.settings") as mock:
        mock.eval_failure_threshold = 0.7
        yield mock


class TestConfidenceScore:
    """Test ConfidenceScore class."""

    def test_initialization(self):
        """Test score initialization."""
        score = ConfidenceScore(
            overall_score=0.85,
            dimensions={"accuracy": 0.9, "relevance": 0.8},
            explanation="Good response",
            suggestions=["Add detail"],
            review_threshold=0.7,
        )

        assert score.overall_score == 0.85
        assert score.dimensions == {"accuracy": 0.9, "relevance": 0.8}
        assert score.explanation == "Good response"
        assert len(score.suggestions) == 1
        assert score.review_threshold == 0.7

    def test_score_clamping(self):
        """Test score is clamped to [0, 1]."""
        # Too high
        score1 = ConfidenceScore(
            overall_score=1.5,
            dimensions={},
            explanation="",
            suggestions=[],
        )
        assert score1.overall_score == 1.0

        # Too low
        score2 = ConfidenceScore(
            overall_score=-0.5,
            dimensions={},
            explanation="",
            suggestions=[],
        )
        assert score2.overall_score == 0.0

    def test_should_review(self):
        """Test should_review property."""
        # High score - no review
        score1 = ConfidenceScore(
            overall_score=0.85,
            dimensions={},
            explanation="",
            suggestions=[],
            review_threshold=0.7,
        )
        assert score1.should_review is False

        # Low score - needs review
        score2 = ConfidenceScore(
            overall_score=0.6,
            dimensions={},
            explanation="",
            suggestions=[],
            review_threshold=0.7,
        )
        assert score2.should_review is True

        # Exact threshold
        score3 = ConfidenceScore(
            overall_score=0.7,
            dimensions={},
            explanation="",
            suggestions=[],
            review_threshold=0.7,
        )
        assert score3.should_review is False

    def test_confidence_level(self):
        """Test confidence_level property."""
        test_cases = [
            (0.95, "very_high"),
            (0.85, "high"),
            (0.75, "high"),
            (0.6, "medium"),
            (0.4, "low"),
        ]

        for score_val, expected_level in test_cases:
            score = ConfidenceScore(
                overall_score=score_val,
                dimensions={},
                explanation="",
                suggestions=[],
            )
            assert score.confidence_level == expected_level

    def test_to_dict(self):
        """Test to_dict method."""
        score = ConfidenceScore(
            overall_score=0.85,
            dimensions={"accuracy": 0.9},
            explanation="Test",
            suggestions=["Improve"],
            review_threshold=0.7,
        )

        result = score.to_dict()

        assert result["overall_score"] == 0.85
        assert result["confidence_level"] == "high"
        assert result["dimensions"] == {"accuracy": 0.9}
        assert result["explanation"] == "Test"
        assert result["suggestions"] == ["Improve"]
        assert result["should_review"] is False

    def test_repr(self):
        """Test string representation."""
        score = ConfidenceScore(
            overall_score=0.85,
            dimensions={},
            explanation="",
            suggestions=[],
        )

        repr_str = repr(score)
        assert "0.85" in repr_str
        assert "high" in repr_str
        assert "False" in repr_str


class TestConfidenceScorer:
    """Test ConfidenceScorer class."""

    def test_initialization(self, mock_settings, mock_centaur_client):
        """Test scorer initialization."""
        scorer = ConfidenceScorer(
            review_threshold=0.8,
            min_confidence=0.6,
        )

        assert scorer.review_threshold == 0.8
        assert scorer.min_confidence == 0.6

    def test_initialization_with_defaults(self, mock_settings, mock_centaur_client):
        """Test initialization with defaults from settings."""
        scorer = ConfidenceScorer()

        assert scorer.review_threshold == 0.7  # From mock settings
        assert scorer.min_confidence == 0.5

    @pytest.mark.asyncio
    async def test_score_response(self, mock_settings, mock_centaur_client):
        """Test scoring a response."""
        mock_centaur_client.calculate_confidence_score = AsyncMock(
            return_value={
                "confidence_score": 0.88,
                "dimensions": {"accuracy": 0.9, "relevance": 0.85},
                "explanation": "High quality response",
                "suggestions": ["Add examples"],
                "metadata": {},
            }
        )

        scorer = ConfidenceScorer()
        result = await scorer.score_response(
            ai_response="Test response",
            context="Test context",
            user_feedback="Good",
        )

        assert isinstance(result, ConfidenceScore)
        assert result.overall_score == 0.88
        assert result.dimensions["accuracy"] == 0.9
        assert result.should_review is False

        # Verify client was called correctly
        mock_centaur_client.calculate_confidence_score.assert_called_once_with(
            ai_response="Test response",
            context="Test context",
            user_feedback="Good",
        )

    @pytest.mark.asyncio
    async def test_batch_score_responses(self, mock_settings, mock_centaur_client):
        """Test batch scoring."""
        mock_centaur_client.calculate_confidence_score = AsyncMock(
            return_value={
                "confidence_score": 0.8,
                "dimensions": {},
                "explanation": "Test",
                "suggestions": [],
                "metadata": {},
            }
        )

        scorer = ConfidenceScorer()
        responses = [
            {"ai_response": "Response 1", "context": "Context 1"},
            {"ai_response": "Response 2", "context": "Context 2", "user_feedback": "Good"},
        ]

        results = await scorer.batch_score_responses(responses)

        assert len(results) == 2
        assert all(isinstance(r, ConfidenceScore) for r in results)
        assert mock_centaur_client.calculate_confidence_score.call_count == 2


class TestAlignmentPrediction:
    """Test AlignmentPrediction class."""

    def test_initialization(self):
        """Test prediction initialization."""
        prediction = AlignmentPrediction(
            predicted_choice="option_a",
            confidence=0.85,
            reasoning="Best fit",
            option_scores={"option_a": 0.85, "option_b": 0.6},
            min_confidence=0.7,
        )

        assert prediction.predicted_choice == "option_a"
        assert prediction.confidence == 0.85
        assert prediction.reasoning == "Best fit"
        assert prediction.option_scores["option_a"] == 0.85

    def test_confidence_clamping(self):
        """Test confidence is clamped to [0, 1]."""
        pred1 = AlignmentPrediction(
            predicted_choice="a",
            confidence=1.5,
            reasoning="",
            option_scores={},
        )
        assert pred1.confidence == 1.0

        pred2 = AlignmentPrediction(
            predicted_choice="a",
            confidence=-0.5,
            reasoning="",
            option_scores={},
        )
        assert pred2.confidence == 0.0

    def test_is_confident(self):
        """Test is_confident property."""
        pred1 = AlignmentPrediction(
            predicted_choice="a",
            confidence=0.8,
            reasoning="",
            option_scores={},
            min_confidence=0.7,
        )
        assert pred1.is_confident is True

        pred2 = AlignmentPrediction(
            predicted_choice="a",
            confidence=0.6,
            reasoning="",
            option_scores={},
            min_confidence=0.7,
        )
        assert pred2.is_confident is False

    def test_confidence_level(self):
        """Test confidence_level property."""
        test_cases = [
            (0.95, "very_high"),
            (0.8, "high"),
            (0.6, "medium"),
            (0.4, "low"),
        ]

        for conf, expected in test_cases:
            pred = AlignmentPrediction(
                predicted_choice="a",
                confidence=conf,
                reasoning="",
                option_scores={},
            )
            assert pred.confidence_level == expected

    def test_to_dict(self):
        """Test to_dict method."""
        prediction = AlignmentPrediction(
            predicted_choice="option_a",
            confidence=0.85,
            reasoning="Best choice",
            option_scores={"option_a": 0.85, "option_b": 0.6},
            min_confidence=0.7,
        )

        result = prediction.to_dict()

        assert result["predicted_choice"] == "option_a"
        assert result["confidence"] == 0.85
        assert result["confidence_level"] == "high"
        assert result["reasoning"] == "Best choice"
        assert result["option_scores"] == {"option_a": 0.85, "option_b": 0.6}
        assert result["is_confident"] is True

    def test_repr(self):
        """Test string representation."""
        prediction = AlignmentPrediction(
            predicted_choice="option_a",
            confidence=0.85,
            reasoning="",
            option_scores={},
        )

        repr_str = repr(prediction)
        assert "option_a" in repr_str
        assert "0.85" in repr_str
        assert "high" in repr_str


class TestDecisionAligner:
    """Test DecisionAligner class."""

    def test_initialization(self, mock_centaur_client):
        """Test aligner initialization."""
        aligner = DecisionAligner(min_confidence=0.6)

        assert aligner.min_confidence == 0.6

    def test_initialization_with_defaults(self, mock_centaur_client):
        """Test initialization with defaults."""
        aligner = DecisionAligner()

        assert aligner.min_confidence == 0.5

    @pytest.mark.asyncio
    async def test_predict_choice(self, mock_centaur_client):
        """Test predicting a choice."""
        mock_centaur_client.predict_alignment = AsyncMock(
            return_value={
                "predicted_choice": "option_a",
                "confidence": 0.88,
                "reasoning": "Best match for user profile",
                "option_scores": {"option_a": 0.88, "option_b": 0.65},
                "metadata": {},
            }
        )

        aligner = DecisionAligner()
        result = await aligner.predict_choice(
            context="Choose option",
            options=["option_a", "option_b"],
            user_profile={"age": 30},
            metadata={"session_id": "123"},
        )

        assert isinstance(result, AlignmentPrediction)
        assert result.predicted_choice == "option_a"
        assert result.confidence == 0.88
        assert result.is_confident is True

        # Verify client was called correctly
        mock_centaur_client.predict_alignment.assert_called_once_with(
            context="Choose option",
            options=["option_a", "option_b"],
            user_profile={"age": 30},
            metadata={"session_id": "123"},
        )

    @pytest.mark.asyncio
    async def test_predict_choice_validation(self, mock_centaur_client):
        """Test validation in predict_choice."""
        aligner = DecisionAligner()

        # Empty options
        with pytest.raises(ValidationError, match="At least one option"):
            await aligner.predict_choice(
                context="test",
                options=[],
            )

    @pytest.mark.asyncio
    async def test_rank_options(self, mock_centaur_client):
        """Test ranking options."""
        mock_centaur_client.predict_alignment = AsyncMock(
            return_value={
                "predicted_choice": "option_a",
                "confidence": 0.88,
                "reasoning": "Test",
                "option_scores": {
                    "option_a": 0.88,
                    "option_b": 0.65,
                    "option_c": 0.45,
                },
                "metadata": {},
            }
        )

        aligner = DecisionAligner()
        ranked = await aligner.rank_options(
            context="Choose",
            options=["option_a", "option_b", "option_c"],
            user_profile={"age": 30},
        )

        # Should be sorted by score descending
        assert len(ranked) == 3
        assert ranked[0]["option"] == "option_a"
        assert ranked[0]["score"] == 0.88
        assert ranked[1]["option"] == "option_b"
        assert ranked[1]["score"] == 0.65
        assert ranked[2]["option"] == "option_c"
        assert ranked[2]["score"] == 0.45

        # Verify sorting
        scores = [item["score"] for item in ranked]
        assert scores == sorted(scores, reverse=True)


class TestUtilityFunctions:
    """Test utility functions."""

    @pytest.mark.asyncio
    async def test_quick_confidence_check(self, mock_centaur_client):
        """Test quick confidence check."""
        mock_centaur_client.calculate_confidence_score = AsyncMock(
            return_value={
                "confidence_score": 0.85,
                "dimensions": {},
                "explanation": "",
                "suggestions": [],
                "metadata": {},
            }
        )

        result = await quick_confidence_check(
            ai_response="Test",
            context="Context",
            threshold=0.7,
        )

        assert result is True  # 0.85 > 0.7

    @pytest.mark.asyncio
    async def test_quick_confidence_check_below_threshold(self, mock_centaur_client):
        """Test quick confidence check below threshold."""
        mock_centaur_client.calculate_confidence_score = AsyncMock(
            return_value={
                "confidence_score": 0.6,
                "dimensions": {},
                "explanation": "",
                "suggestions": [],
                "metadata": {},
            }
        )

        result = await quick_confidence_check(
            ai_response="Test",
            context="Context",
            threshold=0.7,
        )

        assert result is False  # 0.6 < 0.7

    @pytest.mark.asyncio
    async def test_quick_alignment_prediction(self, mock_centaur_client):
        """Test quick alignment prediction."""
        mock_centaur_client.predict_alignment = AsyncMock(
            return_value={
                "predicted_choice": "option_b",
                "confidence": 0.9,
                "reasoning": "",
                "option_scores": {},
                "metadata": {},
            }
        )

        result = await quick_alignment_prediction(
            context="Choose",
            options=["option_a", "option_b"],
            user_profile={"age": 25},
        )

        assert result == "option_b"
