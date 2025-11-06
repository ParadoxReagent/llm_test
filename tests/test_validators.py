"""Tests for validators module."""

import pytest

from llm_compare.validators import (
    MAX_PROMPT_LENGTH,
    MAX_SYSTEM_PROMPT_LENGTH,
    validate_prompt,
)


def test_validate_prompt_accepts_valid_prompt():
    """Test that valid prompts are accepted."""
    assert validate_prompt("Tell me a story.") is True


def test_validate_prompt_accepts_valid_system_prompt():
    """Test that valid system prompts are accepted."""
    assert validate_prompt("You are a helpful assistant.", "system_prompt") is True


def test_validate_prompt_rejects_empty_prompt():
    """Test that empty prompts are rejected."""
    with pytest.raises(ValueError) as exc_info:
        validate_prompt("")
    assert str(exc_info.value) == "❌ Error: Prompt cannot be empty"


def test_validate_prompt_rejects_empty_system_prompt():
    """Test that empty system prompts are rejected."""
    with pytest.raises(ValueError) as exc_info:
        validate_prompt("", "system_prompt")
    assert str(exc_info.value) == "❌ Error: System_prompt cannot be empty"


def test_validate_prompt_rejects_prompt_too_long():
    """Test that overly long prompts are rejected."""
    too_long_prompt = "a" * (MAX_PROMPT_LENGTH + 1)
    with pytest.raises(ValueError) as exc_info:
        validate_prompt(too_long_prompt)
    expected_message = (
        "❌ Error: Prompt is too long "
        f"({len(too_long_prompt)} characters). Maximum allowed: {MAX_PROMPT_LENGTH} characters"
    )
    assert str(exc_info.value) == expected_message


def test_validate_prompt_rejects_system_prompt_too_long():
    """Test that overly long system prompts are rejected."""
    too_long_prompt = "b" * (MAX_SYSTEM_PROMPT_LENGTH + 1)
    with pytest.raises(ValueError) as exc_info:
        validate_prompt(too_long_prompt, "system_prompt")
    expected_message = (
        "❌ Error: System_prompt is too long "
        f"({len(too_long_prompt)} characters). Maximum allowed: {MAX_SYSTEM_PROMPT_LENGTH} characters"
    )
    assert str(exc_info.value) == expected_message


def test_validate_prompt_rejects_prompt_with_null_byte():
    """Test that prompts with null bytes are rejected."""
    with pytest.raises(ValueError) as exc_info:
        validate_prompt("Hello\0World")
    assert str(exc_info.value) == "❌ Error: Prompt contains invalid null bytes"


def test_validate_prompt_rejects_system_prompt_with_null_byte():
    """Test that system prompts with null bytes are rejected."""
    with pytest.raises(ValueError) as exc_info:
        validate_prompt("Intro\0", "system_prompt")
    assert str(exc_info.value) == "❌ Error: System_prompt contains invalid null bytes"
