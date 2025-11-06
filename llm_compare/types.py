"""
Type definitions for LLM Compare.
"""

from typing import Optional, TypedDict


class ModelResponse(TypedDict):
    """Structured response returned for each model invocation."""

    model: str
    response: Optional[str]
    error: Optional[str]
    response_time: Optional[float]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    estimated_cost: Optional[float]
