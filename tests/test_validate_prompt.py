import sys
from pathlib import Path

import pytest

# Ensure the project root is on sys.path for direct module imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm_compare import (
    MAX_PROMPT_LENGTH,
    MAX_SYSTEM_PROMPT_LENGTH,
    validate_prompt,
)


def test_validate_prompt_accepts_valid_prompt():
    assert validate_prompt("Tell me a story.") is True


def test_validate_prompt_accepts_valid_system_prompt():
    assert validate_prompt("You are a helpful assistant.", "system_prompt") is True


def test_validate_prompt_rejects_empty_prompt():
    with pytest.raises(ValueError) as exc_info:
        validate_prompt("")
    assert str(exc_info.value) == "❌ Error: Prompt cannot be empty"


def test_validate_prompt_rejects_empty_system_prompt():
    with pytest.raises(ValueError) as exc_info:
        validate_prompt("", "system_prompt")
    assert str(exc_info.value) == "❌ Error: System_prompt cannot be empty"


def test_validate_prompt_rejects_prompt_too_long():
    too_long_prompt = "a" * (MAX_PROMPT_LENGTH + 1)
    with pytest.raises(ValueError) as exc_info:
        validate_prompt(too_long_prompt)
    expected_message = (
        "❌ Error: Prompt is too long "
        f"({len(too_long_prompt)} characters). Maximum allowed: {MAX_PROMPT_LENGTH} characters"
    )
    assert str(exc_info.value) == expected_message


def test_validate_prompt_rejects_system_prompt_too_long():
    too_long_prompt = "b" * (MAX_SYSTEM_PROMPT_LENGTH + 1)
    with pytest.raises(ValueError) as exc_info:
        validate_prompt(too_long_prompt, "system_prompt")
    expected_message = (
        "❌ Error: System_prompt is too long "
        f"({len(too_long_prompt)} characters). Maximum allowed: {MAX_SYSTEM_PROMPT_LENGTH} characters"
    )
    assert str(exc_info.value) == expected_message


def test_validate_prompt_rejects_prompt_with_null_byte():
    with pytest.raises(ValueError) as exc_info:
        validate_prompt("Hello\0World")
    assert str(exc_info.value) == "❌ Error: Prompt contains invalid null bytes"


def test_validate_prompt_rejects_system_prompt_with_null_byte():
    with pytest.raises(ValueError) as exc_info:
        validate_prompt("Intro\0", "system_prompt")
    assert str(exc_info.value) == "❌ Error: System_prompt contains invalid null bytes"
