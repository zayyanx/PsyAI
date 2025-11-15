"""
Prompt templates for Centaur model integration.

This module provides prompt templates for decision alignment
and confidence scoring.
"""

from psyai.platform.centaur_integration.prompts.templates import (
    ALIGNMENT_PROMPT_TEMPLATE,
    CONFIDENCE_PROMPT_TEMPLATE,
    create_alignment_prompt,
    create_confidence_prompt,
)

__all__ = [
    "ALIGNMENT_PROMPT_TEMPLATE",
    "CONFIDENCE_PROMPT_TEMPLATE",
    "create_alignment_prompt",
    "create_confidence_prompt",
]
