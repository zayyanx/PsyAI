"""
LangSmith integration for PsyAI.

This module provides observability, tracing, and evaluation capabilities
using LangSmith.

Example:
    >>> from psyai.platform.langsmith_integration import (
    ...     get_langsmith_client,
    ...     trace,
    ...     BaseEvaluator,
    ...     EvaluationResult,
    ... )
    >>>
    >>> # Create dataset
    >>> client = get_langsmith_client()
    >>> client.create_dataset("evals", "Evaluation dataset")
    >>>
    >>> # Trace a function
    >>> @trace(name="my_function")
    ... async def my_function(x: int) -> int:
    ...     return x * 2
    >>>
    >>> # Create an evaluator
    >>> class MyEvaluator(BaseEvaluator):
    ...     def evaluate(self, inputs, outputs, reference=None):
    ...         score = calculate_score(outputs)
    ...         return EvaluationResult(score=score, passed=score >= 0.7)
"""

# Client
from psyai.platform.langsmith_integration.client import (
    LangSmithClient,
    get_langsmith_client,
)

# Evaluators
from psyai.platform.langsmith_integration.evaluators import (
    BaseEvaluator,
    ContainsEvaluator,
    EvaluationResult,
    ExactMatchEvaluator,
    LengthEvaluator,
)

# Tracers
from psyai.platform.langsmith_integration.tracers import (
    TraceContext,
    trace,
    trace_agent,
    trace_chain,
    trace_llm_call,
)

__all__ = [
    # Client
    "LangSmithClient",
    "get_langsmith_client",
    # Evaluators
    "BaseEvaluator",
    "EvaluationResult",
    "ExactMatchEvaluator",
    "ContainsEvaluator",
    "LengthEvaluator",
    # Tracers
    "trace",
    "trace_chain",
    "trace_agent",
    "trace_llm_call",
    "TraceContext",
]
