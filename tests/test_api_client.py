"""Tests for API client module."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from llm_compare.api_client import LLMAPIClient


@pytest.mark.asyncio
async def test_get_model_response_success():
    """Test successful model response."""
    client = LLMAPIClient()

    # Mock litellm response
    mock_choice = Mock()
    mock_choice.message.content = "Test response"
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    with patch("llm_compare.api_client.acompletion", new=AsyncMock(return_value=mock_response)):
        result = await client.get_model_response("gpt-4o", "Test prompt")

        assert result["model"] == "gpt-4o"
        assert result["response"] == "Test response"
        assert result["error"] is None
        assert result["response_time"] is not None
        assert result["prompt_tokens"] == 10
        assert result["completion_tokens"] == 5
        assert result["total_tokens"] == 15
        assert result["estimated_cost"] is not None


@pytest.mark.asyncio
async def test_get_model_response_with_system_prompt():
    """Test model response with system prompt."""
    client = LLMAPIClient()

    mock_response = Mock(
        choices=[Mock(message=Mock(content="System-guided response"))],
        usage=Mock(prompt_tokens=20, completion_tokens=8, total_tokens=28),
    )

    with patch("llm_compare.api_client.acompletion", new=AsyncMock(return_value=mock_response)) as mock_acompletion:
        result = await client.get_model_response(
            "test-model", "User message", system_prompt="You are a cat"
        )

        # Verify that system prompt was included
        mock_acompletion.assert_called_once()
        called_messages = mock_acompletion.call_args[1]["messages"]
        assert len(called_messages) == 2
        assert called_messages[0] == {"role": "system", "content": "You are a cat"}
        assert called_messages[1] == {"role": "user", "content": "User message"}

        assert result["response"] == "System-guided response"


@pytest.mark.asyncio
async def test_get_model_response_error():
    """Test model response with error."""
    client = LLMAPIClient()

    with patch(
        "llm_compare.api_client.acompletion",
        new=AsyncMock(side_effect=Exception("API connection error")),
    ):
        result = await client.get_model_response("gpt-4o", "Test prompt")

        assert result["model"] == "gpt-4o"
        assert result["response"] is None
        assert result["error"] == "API connection error"
        assert result["response_time"] is None
        assert result["prompt_tokens"] is None
        assert result["completion_tokens"] is None
        assert result["total_tokens"] is None


@pytest.mark.asyncio
async def test_compare_models():
    """Test comparing multiple models."""
    client = LLMAPIClient()

    # Mock different responses for different models
    def mock_response_factory(model):
        mock_choice = Mock()
        mock_choice.message.content = f"Response from {model}"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        return mock_response

    with patch("llm_compare.api_client.acompletion") as mock_acompletion:
        # Configure mock to return different responses
        mock_acompletion.side_effect = [
            mock_response_factory("model-1"),
            mock_response_factory("model-2"),
        ]

        results = await client.compare_models(
            "Test prompt", ["model-1", "model-2"], temperature=0.7
        )

        assert len(results) == 2
        assert results[0]["model"] == "model-1"
        assert results[1]["model"] == "model-2"
        assert results[0]["error"] is None
        assert results[1]["error"] is None


@pytest.mark.asyncio
async def test_compare_models_with_validation():
    """Test that compare_models validates inputs."""
    client = LLMAPIClient()

    # Test with empty prompt
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        await client.compare_models("", ["model-1"])

    # Test with null byte in prompt
    with pytest.raises(ValueError, match="contains invalid null bytes"):
        await client.compare_models("Hello\0World", ["model-1"])


@pytest.mark.asyncio
async def test_get_model_response_no_usage_data():
    """Test model response when usage data is missing."""
    client = LLMAPIClient()

    mock_response = Mock(choices=[Mock(message=Mock(content="Minimal response"))])
    # Ensure 'usage' attribute does not exist
    del mock_response.usage

    with patch("llm_compare.api_client.acompletion", new=AsyncMock(return_value=mock_response)):
        result = await client.get_model_response("test-model", "Test prompt")

        assert result["response"] == "Minimal response"
        assert result["error"] is None
        assert result["prompt_tokens"] is None
        assert result["completion_tokens"] is None
        assert result["total_tokens"] is None
