"""
Cost tracking and estimation for different LLM models.
"""

from typing import Optional

# Cost per 1M tokens (as of Jan 2025)
# Format: "model_name": (input_cost_per_1m, output_cost_per_1m)
MODEL_COSTS = {
    # OpenAI GPT-4o
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-2024-11-20": (2.50, 10.00),
    "gpt-4o-2024-08-06": (2.50, 10.00),
    "gpt-4o-2024-05-13": (5.00, 15.00),
    # OpenAI GPT-4o Mini
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o-mini-2024-07-18": (0.15, 0.60),
    # OpenAI GPT-4 Turbo
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4-turbo-2024-04-09": (10.00, 30.00),
    "gpt-4-turbo-preview": (10.00, 30.00),
    # OpenAI GPT-4
    "gpt-4": (30.00, 60.00),
    "gpt-4-0613": (30.00, 60.00),
    "gpt-4-0314": (30.00, 60.00),
    # OpenAI GPT-3.5
    "gpt-3.5-turbo": (0.50, 1.50),
    "gpt-3.5-turbo-0125": (0.50, 1.50),
    "gpt-3.5-turbo-1106": (1.00, 2.00),
    # Anthropic Claude 3.5 Sonnet
    "claude-3-5-sonnet-20241022": (3.00, 15.00),
    "claude-3-5-sonnet-20240620": (3.00, 15.00),
    # Anthropic Claude 3 Opus
    "claude-3-opus-20240229": (15.00, 75.00),
    # Anthropic Claude 3 Sonnet
    "claude-3-sonnet-20240229": (3.00, 15.00),
    # Anthropic Claude 3 Haiku
    "claude-3-haiku-20240307": (0.25, 1.25),
    # Google Gemini
    "gemini/gemini-1.5-pro": (1.25, 5.00),
    "gemini/gemini-1.5-pro-latest": (1.25, 5.00),
    "gemini/gemini-1.5-flash": (0.075, 0.30),
    "gemini/gemini-1.5-flash-latest": (0.075, 0.30),
    "gemini/gemini-pro": (0.50, 1.50),
    # Add more models as needed
}


def estimate_cost(
    model: str, prompt_tokens: Optional[int], completion_tokens: Optional[int]
) -> Optional[float]:
    """
    Estimate the cost for a model invocation.

    Args:
        model: Model identifier
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens

    Returns:
        Estimated cost in USD, or None if tokens not available or model not in pricing database
    """
    if prompt_tokens is None or completion_tokens is None:
        return None

    # Normalize model name (handle litellm prefixes)
    normalized_model = model.lower()
    for prefix in ["openai/", "anthropic/", "google/", "azure/"]:
        if normalized_model.startswith(prefix):
            normalized_model = normalized_model[len(prefix) :]

    # Look up costs
    costs = MODEL_COSTS.get(normalized_model)
    if not costs:
        # Try to find a partial match (e.g., "gpt-4o-2024-11-20" should match "gpt-4o")
        for known_model, known_costs in MODEL_COSTS.items():
            if normalized_model.startswith(known_model):
                costs = known_costs
                break

    if not costs:
        return None

    input_cost_per_1m, output_cost_per_1m = costs

    # Calculate cost
    input_cost = (prompt_tokens / 1_000_000) * input_cost_per_1m
    output_cost = (completion_tokens / 1_000_000) * output_cost_per_1m

    return input_cost + output_cost


def format_cost(cost: Optional[float]) -> str:
    """
    Format cost for display.

    Args:
        cost: Cost in USD

    Returns:
        Formatted cost string
    """
    if cost is None:
        return "N/A"

    if cost < 0.0001:
        return f"${cost:.6f}"
    elif cost < 0.01:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"
