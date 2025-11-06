"""Tests for cost tracker module."""

import pytest

from llm_compare.cost_tracker import estimate_cost, format_cost


def test_estimate_cost_gpt4o():
    """Test cost estimation for GPT-4o."""
    cost = estimate_cost("gpt-4o", 1000, 500)
    assert cost is not None
    # 1000 * 2.50 / 1M + 500 * 10.00 / 1M = 0.0025 + 0.005 = 0.0075
    assert abs(cost - 0.0075) < 0.0001


def test_estimate_cost_gpt4o_mini():
    """Test cost estimation for GPT-4o-mini."""
    cost = estimate_cost("gpt-4o-mini", 1000, 500)
    assert cost is not None
    # 1000 * 0.15 / 1M + 500 * 0.60 / 1M = 0.00015 + 0.0003 = 0.00045
    assert abs(cost - 0.00045) < 0.00001


def test_estimate_cost_claude():
    """Test cost estimation for Claude."""
    cost = estimate_cost("claude-3-5-sonnet-20241022", 1000, 500)
    assert cost is not None
    # 1000 * 3.00 / 1M + 500 * 15.00 / 1M = 0.003 + 0.0075 = 0.0105
    assert abs(cost - 0.0105) < 0.0001


def test_estimate_cost_gemini():
    """Test cost estimation for Gemini."""
    cost = estimate_cost("gemini/gemini-1.5-flash", 1000, 500)
    assert cost is not None
    # 1000 * 0.075 / 1M + 500 * 0.30 / 1M = 0.000075 + 0.00015 = 0.000225
    assert abs(cost - 0.000225) < 0.000001


def test_estimate_cost_with_prefix():
    """Test cost estimation with provider prefix."""
    cost = estimate_cost("openai/gpt-4o", 1000, 500)
    assert cost is not None
    assert abs(cost - 0.0075) < 0.0001


def test_estimate_cost_unknown_model():
    """Test cost estimation for unknown model."""
    cost = estimate_cost("unknown-model", 1000, 500)
    assert cost is None


def test_estimate_cost_none_tokens():
    """Test cost estimation with None tokens."""
    cost = estimate_cost("gpt-4o", None, 500)
    assert cost is None

    cost = estimate_cost("gpt-4o", 1000, None)
    assert cost is None


def test_format_cost_small():
    """Test cost formatting for small amounts."""
    assert format_cost(0.000001) == "$0.000001"
    assert format_cost(0.00001) == "$0.000010"


def test_format_cost_medium():
    """Test cost formatting for medium amounts."""
    assert format_cost(0.001) == "$0.0010"
    assert format_cost(0.0075) == "$0.0075"


def test_format_cost_large():
    """Test cost formatting for large amounts."""
    assert format_cost(0.05) == "$0.05"
    assert format_cost(1.50) == "$1.50"


def test_format_cost_none():
    """Test cost formatting for None."""
    assert format_cost(None) == "N/A"
