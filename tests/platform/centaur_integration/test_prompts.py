"""Tests for Centaur prompt templates."""

import pytest

from psyai.platform.centaur_integration.prompts import (
    ALIGNMENT_PROMPT_TEMPLATE,
    CONFIDENCE_PROMPT_TEMPLATE,
    create_alignment_prompt,
    create_confidence_prompt,
)
from psyai.platform.centaur_integration.prompts.templates import (
    HITL_REVIEW_PROMPT_TEMPLATE,
    create_eval_quality_prompt,
    create_hitl_review_prompt,
)


class TestAlignmentPrompt:
    """Test alignment prompt creation."""

    def test_template_exists(self):
        """Test that template is defined."""
        assert ALIGNMENT_PROMPT_TEMPLATE is not None
        assert len(ALIGNMENT_PROMPT_TEMPLATE) > 0
        assert "Context:" in ALIGNMENT_PROMPT_TEMPLATE
        assert "Available Options:" in ALIGNMENT_PROMPT_TEMPLATE

    def test_create_alignment_prompt_basic(self):
        """Test basic alignment prompt creation."""
        prompt = create_alignment_prompt(
            context="Choose a vacation destination",
            options=["Beach", "Mountains", "City"],
        )

        assert "Choose a vacation destination" in prompt
        assert "1. Beach" in prompt
        assert "2. Mountains" in prompt
        assert "3. City" in prompt
        assert "Not provided" in prompt  # No user profile

    def test_create_alignment_prompt_with_profile(self):
        """Test alignment prompt with user profile."""
        prompt = create_alignment_prompt(
            context="Choose a laptop",
            options=["MacBook", "ThinkPad"],
            user_profile={"age": 30, "profession": "developer"},
        )

        assert "Choose a laptop" in prompt
        assert "MacBook" in prompt
        assert "ThinkPad" in prompt
        assert "age: 30" in prompt
        assert "profession: developer" in prompt
        assert "Not provided" not in prompt

    def test_create_alignment_prompt_single_option(self):
        """Test with single option."""
        prompt = create_alignment_prompt(
            context="Test",
            options=["Only Option"],
        )

        assert "1. Only Option" in prompt

    def test_create_alignment_prompt_many_options(self):
        """Test with many options."""
        options = [f"Option {i}" for i in range(1, 11)]
        prompt = create_alignment_prompt(
            context="Choose",
            options=options,
        )

        for i, opt in enumerate(options, 1):
            assert f"{i}. {opt}" in prompt


class TestConfidencePrompt:
    """Test confidence prompt creation."""

    def test_template_exists(self):
        """Test that template is defined."""
        assert CONFIDENCE_PROMPT_TEMPLATE is not None
        assert len(CONFIDENCE_PROMPT_TEMPLATE) > 0
        assert "Context/Prompt:" in CONFIDENCE_PROMPT_TEMPLATE
        assert "AI Response:" in CONFIDENCE_PROMPT_TEMPLATE

    def test_create_confidence_prompt_basic(self):
        """Test basic confidence prompt creation."""
        prompt = create_confidence_prompt(
            ai_response="Python is great for ML",
            context="What's the best language?",
        )

        assert "Python is great for ML" in prompt
        assert "What's the best language?" in prompt
        assert "No feedback provided" in prompt

    def test_create_confidence_prompt_with_feedback(self):
        """Test confidence prompt with user feedback."""
        prompt = create_confidence_prompt(
            ai_response="Test response",
            context="Test context",
            user_feedback="Very helpful, thanks!",
        )

        assert "Test response" in prompt
        assert "Test context" in prompt
        assert "Very helpful, thanks!" in prompt
        assert "No feedback provided" not in prompt

    def test_create_confidence_prompt_empty_feedback(self):
        """Test with empty string feedback."""
        prompt = create_confidence_prompt(
            ai_response="Response",
            context="Context",
            user_feedback="",
        )

        # Empty string feedback should be preserved, not replaced
        assert "No feedback provided" not in prompt


class TestHITLReviewPrompt:
    """Test HITL review prompt creation."""

    def test_template_exists(self):
        """Test that template is defined."""
        assert HITL_REVIEW_PROMPT_TEMPLATE is not None
        assert "AI Decision:" in HITL_REVIEW_PROMPT_TEMPLATE
        assert "Should this decision be reviewed" in HITL_REVIEW_PROMPT_TEMPLATE

    def test_create_hitl_review_prompt_basic(self):
        """Test basic HITL review prompt."""
        prompt = create_hitl_review_prompt(
            ai_decision="Approve loan application",
            context="User applied for $50k loan",
        )

        assert "Approve loan application" in prompt
        assert "User applied for $50k loan" in prompt
        assert "None provided" in prompt

    def test_create_hitl_review_prompt_with_metadata(self):
        """Test HITL review prompt with metadata."""
        prompt = create_hitl_review_prompt(
            ai_decision="Deny access",
            context="Security access request",
            metadata={
                "risk_level": "high",
                "user_role": "contractor",
                "requested_access": "production_db",
            },
        )

        assert "Deny access" in prompt
        assert "Security access request" in prompt
        assert "risk_level: high" in prompt
        assert "user_role: contractor" in prompt
        assert "requested_access: production_db" in prompt

    def test_create_hitl_review_prompt_empty_metadata(self):
        """Test with empty metadata dict."""
        prompt = create_hitl_review_prompt(
            ai_decision="Decision",
            context="Context",
            metadata={},
        )

        assert "Decision" in prompt
        assert "Context" in prompt


class TestEvalQualityPrompt:
    """Test evaluation quality prompt creation."""

    def test_create_eval_quality_prompt(self):
        """Test eval quality prompt creation."""
        prompt = create_eval_quality_prompt(
            input_data={"query": "What is 2+2?"},
            expected_output={"answer": "4"},
            actual_output={"answer": "4"},
        )

        assert "query" in prompt
        assert "2+2" in prompt
        assert "answer" in prompt
        assert "4" in prompt

    def test_create_eval_quality_prompt_mismatch(self):
        """Test with mismatched output."""
        prompt = create_eval_quality_prompt(
            input_data={"query": "Capital of France?"},
            expected_output={"answer": "Paris"},
            actual_output={"answer": "London"},
        )

        assert "Capital of France" in prompt
        assert "Paris" in prompt
        assert "London" in prompt

    def test_create_eval_quality_prompt_complex_data(self):
        """Test with complex nested data."""
        prompt = create_eval_quality_prompt(
            input_data={
                "query": "Test",
                "context": {"user": "john", "session": "123"},
            },
            expected_output={
                "answer": "Response",
                "metadata": {"confidence": 0.9},
            },
            actual_output={
                "answer": "Response",
                "metadata": {"confidence": 0.85},
            },
        )

        # Should contain string representations
        assert "query" in prompt or "Test" in prompt
        assert "john" in prompt
        assert "confidence" in prompt or "0.9" in prompt or "0.85" in prompt


class TestPromptFormatting:
    """Test prompt formatting and structure."""

    def test_alignment_prompt_formatting(self):
        """Test alignment prompt is well-formatted."""
        prompt = create_alignment_prompt(
            context="Test context",
            options=["A", "B", "C"],
            user_profile={"key": "value"},
        )

        # Should be multi-line
        assert "\n" in prompt

        # Should have proper sections
        lines = prompt.split("\n")
        assert len(lines) > 5

    def test_confidence_prompt_formatting(self):
        """Test confidence prompt is well-formatted."""
        prompt = create_confidence_prompt(
            ai_response="Test response",
            context="Test context",
            user_feedback="Feedback",
        )

        # Should be multi-line
        assert "\n" in prompt

        # Should have sections
        lines = prompt.split("\n")
        assert len(lines) > 5

    def test_prompts_are_strings(self):
        """Test all prompts return strings."""
        prompts = [
            create_alignment_prompt("ctx", ["a"]),
            create_confidence_prompt("resp", "ctx"),
            create_hitl_review_prompt("dec", "ctx"),
            create_eval_quality_prompt({}, {}, {}),
        ]

        for prompt in prompts:
            assert isinstance(prompt, str)
            assert len(prompt) > 0

    def test_prompts_preserve_special_characters(self):
        """Test prompts preserve special characters."""
        special_text = "Test with $pecial ch@rs & symbols: 100%!"

        prompt1 = create_alignment_prompt(
            context=special_text,
            options=["Option"],
        )
        assert special_text in prompt1

        prompt2 = create_confidence_prompt(
            ai_response=special_text,
            context="Context",
        )
        assert special_text in prompt2

    def test_prompts_handle_unicode(self):
        """Test prompts handle unicode characters."""
        unicode_text = "Test with émojis 😀 and spëcial chàracters"

        prompt = create_alignment_prompt(
            context=unicode_text,
            options=["Option"],
        )
        assert unicode_text in prompt

    def test_prompts_handle_long_text(self):
        """Test prompts handle very long text."""
        long_text = "A" * 10000

        prompt = create_confidence_prompt(
            ai_response=long_text,
            context="Context",
        )

        assert long_text in prompt
        assert len(prompt) > 10000
