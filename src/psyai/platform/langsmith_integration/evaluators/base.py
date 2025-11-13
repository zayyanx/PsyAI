"""
Base evaluator classes and framework.

This module provides the base classes and interfaces for building evaluators.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from psyai.core.logging import get_logger

logger = get_logger(__name__)


class EvaluationResult:
    """
    Result of an evaluation.

    Attributes:
        score: Numeric score (0.0 to 1.0)
        passed: Whether the evaluation passed
        reason: Explanation of the result
        metadata: Additional metadata
    """

    def __init__(
        self,
        score: float,
        passed: bool,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize evaluation result.

        Args:
            score: Score between 0.0 and 1.0
            passed: Whether evaluation passed
            reason: Optional explanation
            metadata: Optional metadata
        """
        self.score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        self.passed = passed
        self.reason = reason
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "score": self.score,
            "passed": self.passed,
            "reason": self.reason,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        """String representation."""
        status = "PASS" if self.passed else "FAIL"
        return f"EvaluationResult({status}, score={self.score:.2f})"


class BaseEvaluator(ABC):
    """
    Base class for all evaluators.

    Subclass this to create custom evaluators.

    Example:
        >>> class MyEvaluator(BaseEvaluator):
        ...     def evaluate(self, inputs, outputs, reference=None):
        ...         score = calculate_score(outputs)
        ...         return EvaluationResult(
        ...             score=score,
        ...             passed=score >= self.threshold
        ...         )
    """

    def __init__(
        self,
        name: str,
        threshold: float = 0.7,
        description: Optional[str] = None,
    ):
        """
        Initialize evaluator.

        Args:
            name: Evaluator name
            threshold: Passing threshold (0.0 to 1.0)
            description: Optional description
        """
        self.name = name
        self.threshold = max(0.0, min(1.0, threshold))
        self.description = description or f"{name} evaluator"

        logger.debug("evaluator_initialized", name=name, threshold=threshold)

    @abstractmethod
    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        reference: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        """
        Evaluate the outputs.

        Args:
            inputs: Input data
            outputs: Output data to evaluate
            reference: Optional reference/expected outputs

        Returns:
            EvaluationResult

        Note:
            This method must be implemented by subclasses.
        """
        pass

    async def aevaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        reference: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        """
        Async version of evaluate.

        Default implementation calls the sync version.
        Override for true async evaluation.

        Args:
            inputs: Input data
            outputs: Output data to evaluate
            reference: Optional reference/expected outputs

        Returns:
            EvaluationResult
        """
        return self.evaluate(inputs, outputs, reference)

    def __call__(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        reference: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        """
        Make evaluator callable.

        Args:
            inputs: Input data
            outputs: Output data to evaluate
            reference: Optional reference/expected outputs

        Returns:
            EvaluationResult
        """
        return self.evaluate(inputs, outputs, reference)


class ExactMatchEvaluator(BaseEvaluator):
    """
    Evaluator that checks for exact match with reference output.

    Example:
        >>> evaluator = ExactMatchEvaluator()
        >>> result = evaluator.evaluate(
        ...     inputs={"query": "2+2"},
        ...     outputs={"answer": "4"},
        ...     reference={"answer": "4"}
        ... )
        >>> print(result.passed)  # True
    """

    def __init__(
        self,
        output_key: str = "answer",
        case_sensitive: bool = False,
    ):
        """
        Initialize exact match evaluator.

        Args:
            output_key: Key to check in outputs
            case_sensitive: Whether to do case-sensitive matching
        """
        super().__init__(
            name="exact_match",
            threshold=1.0,
            description="Exact match evaluator",
        )
        self.output_key = output_key
        self.case_sensitive = case_sensitive

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        reference: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        """Evaluate exact match."""
        if reference is None:
            return EvaluationResult(
                score=0.0,
                passed=False,
                reason="No reference output provided",
            )

        actual = str(outputs.get(self.output_key, ""))
        expected = str(reference.get(self.output_key, ""))

        if not self.case_sensitive:
            actual = actual.lower()
            expected = expected.lower()

        matches = actual == expected
        score = 1.0 if matches else 0.0

        return EvaluationResult(
            score=score,
            passed=matches,
            reason=f"Expected: '{expected}', Got: '{actual}'" if not matches else None,
        )


class ContainsEvaluator(BaseEvaluator):
    """
    Evaluator that checks if output contains expected substring.

    Example:
        >>> evaluator = ContainsEvaluator(expected_substring="PsyAI")
        >>> result = evaluator.evaluate(
        ...     inputs={"query": "What is this?"},
        ...     outputs={"answer": "This is PsyAI, an AI framework"}
        ... )
        >>> print(result.passed)  # True
    """

    def __init__(
        self,
        expected_substring: str,
        output_key: str = "answer",
        case_sensitive: bool = False,
    ):
        """
        Initialize contains evaluator.

        Args:
            expected_substring: Substring to look for
            output_key: Key to check in outputs
            case_sensitive: Whether to do case-sensitive matching
        """
        super().__init__(
            name="contains",
            threshold=1.0,
            description=f"Contains '{expected_substring}' evaluator",
        )
        self.expected_substring = expected_substring
        self.output_key = output_key
        self.case_sensitive = case_sensitive

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        reference: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        """Evaluate if output contains substring."""
        actual = str(outputs.get(self.output_key, ""))
        expected = self.expected_substring

        if not self.case_sensitive:
            actual = actual.lower()
            expected = expected.lower()

        contains = expected in actual
        score = 1.0 if contains else 0.0

        return EvaluationResult(
            score=score,
            passed=contains,
            reason=f"Output does not contain '{self.expected_substring}'" if not contains else None,
        )


class LengthEvaluator(BaseEvaluator):
    """
    Evaluator that checks output length.

    Example:
        >>> evaluator = LengthEvaluator(min_length=10, max_length=100)
        >>> result = evaluator.evaluate(
        ...     inputs={"query": "Explain"},
        ...     outputs={"answer": "This is a short answer"}
        ... )
        >>> print(result.passed)  # True if length is in range
    """

    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        output_key: str = "answer",
    ):
        """
        Initialize length evaluator.

        Args:
            min_length: Minimum acceptable length
            max_length: Maximum acceptable length
            output_key: Key to check in outputs
        """
        super().__init__(
            name="length",
            threshold=1.0,
            description="Length evaluator",
        )
        self.min_length = min_length
        self.max_length = max_length
        self.output_key = output_key

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        reference: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        """Evaluate output length."""
        actual = str(outputs.get(self.output_key, ""))
        length = len(actual)

        passed = True
        reasons = []

        if self.min_length is not None and length < self.min_length:
            passed = False
            reasons.append(f"Too short: {length} < {self.min_length}")

        if self.max_length is not None and length > self.max_length:
            passed = False
            reasons.append(f"Too long: {length} > {self.max_length}")

        score = 1.0 if passed else 0.0

        return EvaluationResult(
            score=score,
            passed=passed,
            reason="; ".join(reasons) if reasons else None,
            metadata={"length": length},
        )
