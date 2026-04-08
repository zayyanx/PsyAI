"""
Platform layer for PsyAI.

This module provides platform services that features depend on.
"""

__all__ = []

# Vertex AI integration (primary)
#
# Keep these imports optional so API-only workflows (for example local tests or
# non-Vertex integrations) do not fail at package import time when heavy
# optional dependencies are unavailable.
try:
    from psyai.platform.vertexai_integration import (
        AgentBuilder,
        AgentResponse,
        ConversationalAgent,
        CustomMetricEvaluator,
        Document,
        EvaluationResult,
        FunctionCallingAgent,
        SimpleAgent,
        VertexAIClient,
        VertexEmbeddingService,
        VertexEvaluator,
        VertexVectorStoreManager,
        get_vertex_embedding_service,
        get_vertex_evaluator,
        get_vertexai_client,
    )

    __all__ = [
        # Vertex AI - Client
        "VertexAIClient",
        "get_vertexai_client",
        # Vertex AI - Agents
        "AgentBuilder",
        "AgentResponse",
        "ConversationalAgent",
        "FunctionCallingAgent",
        "SimpleAgent",
        # Vertex AI - RAG
        "Document",
        "VertexEmbeddingService",
        "VertexVectorStoreManager",
        "get_vertex_embedding_service",
        # Vertex AI - Evaluation
        "CustomMetricEvaluator",
        "EvaluationResult",
        "VertexEvaluator",
        "get_vertex_evaluator",
    ]
except Exception:
    # Intentionally suppress import-time dependency failures here.
    # Concrete modules (e.g., vertexai_integration) still raise explicit errors
    # when imported directly without required dependencies.
    pass
