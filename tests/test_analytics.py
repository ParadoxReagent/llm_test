"""Tests for analytics module."""

import pytest

from llm_compare.analytics import ComparisonAnalytics
from llm_compare.types import ModelResponse


@pytest.fixture
def sample_results():
    """Fixture providing sample results."""
    return [
        ModelResponse(
            model="model-1",
            response="Response 1",
            error=None,
            response_time=1.5,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost=0.001,
        ),
        ModelResponse(
            model="model-2",
            response="Response 2",
            error=None,
            response_time=2.0,
            prompt_tokens=120,
            completion_tokens=60,
            total_tokens=180,
            estimated_cost=0.0015,
        ),
        ModelResponse(
            model="model-3",
            response=None,
            error="API Error",
            response_time=None,
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            estimated_cost=None,
        ),
    ]


def test_get_fastest_model(sample_results):
    """Test finding the fastest model."""
    analytics = ComparisonAnalytics(sample_results)
    assert analytics.get_fastest_model() == "model-1"


def test_get_slowest_model(sample_results):
    """Test finding the slowest model."""
    analytics = ComparisonAnalytics(sample_results)
    assert analytics.get_slowest_model() == "model-2"


def test_get_average_response_time(sample_results):
    """Test calculating average response time."""
    analytics = ComparisonAnalytics(sample_results)
    avg_time = analytics.get_average_response_time()
    assert avg_time is not None
    assert abs(avg_time - 1.75) < 0.01  # (1.5 + 2.0) / 2


def test_get_most_token_efficient(sample_results):
    """Test finding the most token-efficient model."""
    analytics = ComparisonAnalytics(sample_results)
    assert analytics.get_most_token_efficient() == "model-1"


def test_get_least_expensive(sample_results):
    """Test finding the least expensive model."""
    analytics = ComparisonAnalytics(sample_results)
    assert analytics.get_least_expensive() == "model-1"


def test_get_total_cost(sample_results):
    """Test calculating total cost."""
    analytics = ComparisonAnalytics(sample_results)
    total_cost = analytics.get_total_cost()
    assert total_cost is not None
    assert abs(total_cost - 0.0025) < 0.0001  # 0.001 + 0.0015


def test_get_success_rate(sample_results):
    """Test calculating success rate."""
    analytics = ComparisonAnalytics(sample_results)
    success_rate = analytics.get_success_rate()
    assert abs(success_rate - 66.67) < 0.1  # 2 out of 3 successful


def test_get_summary(sample_results):
    """Test generating summary."""
    analytics = ComparisonAnalytics(sample_results)
    summary = analytics.get_summary()
    assert "Success Rate" in summary
    assert "Fastest Model: model-1" in summary
    assert "Slowest Model: model-2" in summary
    assert "Total Cost" in summary


def test_analytics_with_all_errors():
    """Test analytics when all models have errors."""
    results = [
        ModelResponse(
            model="model-1",
            response=None,
            error="Error 1",
            response_time=None,
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            estimated_cost=None,
        ),
        ModelResponse(
            model="model-2",
            response=None,
            error="Error 2",
            response_time=None,
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            estimated_cost=None,
        ),
    ]

    analytics = ComparisonAnalytics(results)
    assert analytics.get_fastest_model() is None
    assert analytics.get_slowest_model() is None
    assert analytics.get_average_response_time() is None
    assert analytics.get_most_token_efficient() is None
    assert analytics.get_least_expensive() is None
    assert analytics.get_total_cost() is None
    assert analytics.get_success_rate() == 0.0


def test_analytics_with_empty_results():
    """Test analytics with empty results."""
    analytics = ComparisonAnalytics([])
    assert analytics.get_success_rate() == 0.0
