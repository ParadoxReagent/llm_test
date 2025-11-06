"""
Input validation functions.
"""

# Security constants
MAX_PROMPT_LENGTH = 50000  # Maximum characters for a prompt
MAX_SYSTEM_PROMPT_LENGTH = 10000  # Maximum characters for system prompt


def validate_prompt(prompt: str, prompt_type: str = "prompt") -> bool:
    """
    Validate prompt input for security and sanity.

    Args:
        prompt: The prompt to validate
        prompt_type: Type of prompt ("prompt" or "system_prompt")

    Returns:
        True if valid

    Raises:
        ValueError: If prompt is invalid
    """
    if not prompt:
        raise ValueError(f"❌ Error: {prompt_type.capitalize()} cannot be empty")

    # Check length based on prompt type
    max_length = (
        MAX_SYSTEM_PROMPT_LENGTH if prompt_type == "system_prompt" else MAX_PROMPT_LENGTH
    )
    if len(prompt) > max_length:
        raise ValueError(
            f"❌ Error: {prompt_type.capitalize()} is too long ({len(prompt)} characters). "
            f"Maximum allowed: {max_length} characters"
        )

    # Strip any null bytes (potential injection attack)
    if "\0" in prompt:
        raise ValueError(
            f"❌ Error: {prompt_type.capitalize()} contains invalid null bytes"
        )

    return True
