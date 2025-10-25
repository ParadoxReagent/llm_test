import sys
from pathlib import Path
import pytest

# Ensure the project root is on sys.path for direct module imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from unittest.mock import Mock, patch
from llm_compare import get_model_response, export_results, main


# Tests for get_model_response
@patch("llm_compare.completion")
def test_get_model_response_success(mock_completion):
    # Mock litellm response
    mock_choice = Mock()
    mock_choice.message.content = "Test response"
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15
    mock_completion.return_value = mock_response

    model = "gpt-4"
    prompt = "Test prompt"
    result = get_model_response(model, prompt)

    assert result["model"] == model
    assert result["response"] == "Test response"
    assert result["error"] is None
    assert result["response_time"] is not None
    assert result["prompt_tokens"] == 10
    assert result["completion_tokens"] == 5
    assert result["total_tokens"] == 15


@patch("llm_compare.completion")
def test_get_model_response_with_system_prompt(mock_completion):
    mock_completion.return_value = Mock(
        choices=[Mock(message=Mock(content="System-guided response"))],
        usage=Mock(prompt_tokens=20, completion_tokens=8, total_tokens=28),
    )

    result = get_model_response(
        "test-model", "User message", system_prompt="You are a cat"
    )

    # Verify that the system prompt was included in the messages
    mock_completion.assert_called_once()
    called_messages = mock_completion.call_args[1]["messages"]
    assert len(called_messages) == 2
    assert called_messages[0] == {"role": "system", "content": "You are a cat"}
    assert called_messages[1] == {"role": "user", "content": "User message"}

    assert result["response"] == "System-guided response"


@patch("llm_compare.completion")
def test_get_model_response_api_error(mock_completion):
    # Mock an API error
    error_message = "API connection error"
    mock_completion.side_effect = Exception(error_message)

    model = "gpt-4"
    prompt = "Test prompt"
    result = get_model_response(model, prompt)

    assert result["model"] == model
    assert result["response"] is None
    assert result["error"] == error_message
    assert result["response_time"] is None
    assert result["prompt_tokens"] is None
    assert result["completion_tokens"] is None
    assert result["total_tokens"] is None


# Tests for main function (CLI)
@patch("llm_compare.interactive_mode")
def test_main_interactive_mode(mock_interactive, monkeypatch):
    # Simulate running with no prompt
    monkeypatch.setattr(sys, "argv", ["llm_compare.py"])
    # Mock the API key to prevent premature exit
    monkeypatch.setenv("LITELLM_API_KEY", "fake_key")
    main()
    mock_interactive.assert_called_once()


@patch("llm_compare.compare_models")
def test_main_single_prompt_mode(mock_compare, monkeypatch):
    # Simulate running with a prompt
    monkeypatch.setattr(
        sys, "argv", ["llm_compare.py", "-p", "Hello"]
    )
    monkeypatch.setenv("LITELLM_API_KEY", "fake_key")
    main()
    mock_compare.assert_called_once()
    # Check if the prompt argument was passed correctly
    assert mock_compare.call_args[0][0] == "Hello"


@patch("llm_compare.compare_models")
def test_main_model_selection(mock_compare, monkeypatch):
    # Test custom model selection
    monkeypatch.setattr(
        sys,
        "argv",
        ["llm_compare.py", "-p", "Test", "-m", "model-a", "model-b"],
    )
    monkeypatch.setenv("LITELLM_API_KEY", "fake_key")
    main()
    mock_compare.assert_called_once()
    assert mock_compare.call_args[0][1] == ["model-a", "model-b"]


@patch("llm_compare.compare_models")
def test_main_preset_selection(mock_compare, monkeypatch):
    # Test preset model selection
    monkeypatch.setattr(
        sys, "argv", ["llm_compare.py", "-p", "Test", "--preset", "creative"]
    )
    monkeypatch.setenv("LITELLM_API_KEY", "fake_key")
    main()
    mock_compare.assert_called_once()
    # Ensure it uses the creative models list (you might need to import it or mock it)
    from models import CREATIVE_MODELS

    assert mock_compare.call_args[0][1] == CREATIVE_MODELS


def test_main_missing_api_key(monkeypatch, capsys):
    # Ensure it exits if API key is not set
    monkeypatch.setattr(sys, "argv", ["llm_compare.py", "-p", "Test"])
    # Unset the API key
    monkeypatch.delenv("LITELLM_API_KEY", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "LITELLM_API_KEY not found" in captured.out


def test_main_invalid_temperature(monkeypatch, capsys):
    # Ensure it exits with invalid temperature
    monkeypatch.setattr(
        sys, "argv", ["llm_compare.py", "-p", "Test", "-t", "1.5"]
    )
    monkeypatch.setenv("LITELLM_API_KEY", "fake_key")

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Temperature must be between 0 and 1" in captured.out


@patch("llm_compare.export_results")
@patch("llm_compare.compare_models")
def test_main_export_functionality(mock_compare, mock_export, monkeypatch):
    # Simulate running with export arguments
    output_file = "output.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["llm_compare.py", "-p", "Export test", "-o", output_file],
    )
    monkeypatch.setenv("LITELLM_API_KEY", "fake_key")
    # Mock the return value of compare_models
    mock_compare.return_value = [
        {
            "model": "test",
            "response": "data",
            "error": None,
            "response_time": 1.0,
            "prompt_tokens": 1,
            "completion_tokens": 1,
            "total_tokens": 2,
        }
    ]

    main()

    mock_export.assert_called_once()
    # Check that export_results was called with the correct arguments
    assert mock_export.call_args[0][3] == output_file  # output_file path
    assert mock_export.call_args[0][2] == "json"  # format


# Tests for export_results
@pytest.fixture
def mock_results():
    """Fixture for mock results data."""
    return [
        {
            "model": "model-1",
            "response": "Response from model 1",
            "error": None,
            "response_time": 1.23,
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        },
        {
            "model": "model-2",
            "response": None,
            "error": "API error",
            "response_time": None,
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        },
    ]


def test_export_results_json(tmp_path, mock_results):
    output_file = tmp_path / "results.json"
    export_results(mock_results, "Test prompt", "json", str(output_file))

    assert output_file.exists()
    with open(output_file, "r") as f:
        data = f.read()
        assert '"prompt": "Test prompt"' in data
        assert '"model": "model-1"' in data
        assert '"response": "Response from model 1"' in data


def test_export_results_csv(tmp_path, mock_results):
    output_file = tmp_path / "results.csv"
    export_results(mock_results, "Test prompt", "csv", str(output_file))

    assert output_file.exists()
    with open(output_file, "r") as f:
        data = f.read()
        assert "Timestamp,Prompt,System Prompt,Model,Response,Response Time (s)" in data
        assert "model-1,Response from model 1,1.23" in data
        assert "model-2,,," in data


def test_export_results_markdown(tmp_path, mock_results):
    output_file = tmp_path / "results.md"
    prompt = "Summarize this for me"
    system_prompt = "Act like a pirate"
    export_results(
        mock_results, prompt, "markdown", str(output_file), system_prompt
    )

    assert output_file.exists()
    with open(output_file, "r") as f:
        data = f.read()
        assert f"**Prompt:** {prompt}" in data
        assert f"**System Prompt:** {system_prompt}" in data
        assert "## Model 1: model-1" in data
        assert "**Response Time:** 1.23s" in data
        assert "**Response:**\n\nResponse from model 1" in data
        assert "## Model 2: model-2" in data
        assert "**Error:** API error" in data


def test_export_results_permission_error(mock_results, capsys):
    # Use a path that is likely to cause a permission error
    # In a sandboxed environment, this might be tricky. Let's mock it.
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        export_results(mock_results, "prompt", "json", "/dev/null/test.json")
        captured = capsys.readouterr()
        assert "❌ Error: Permission denied" in captured.out


def test_export_results_os_error(mock_results, capsys):
    # Mock an OSError
    with patch("builtins.open", side_effect=OSError("Disk full")):
        export_results(mock_results, "prompt", "csv", "nonexistent/path/results.csv")
        captured = capsys.readouterr()
        assert "❌ Error: Failed to write" in captured.out


@patch("llm_compare.completion")
def test_get_model_response_no_usage_data(mock_completion):
    # Simulate a response where usage data is missing
    mock_response = Mock(
        choices=[Mock(message=Mock(content="Minimal response"))],
    )
    # Ensure 'usage' attribute does not exist
    del mock_response.usage
    mock_completion.return_value = mock_response

    result = get_model_response("test-model", "Test prompt")

    assert result["response"] == "Minimal response"
    assert result["error"] is None
    assert result["prompt_tokens"] is None
    assert result["completion_tokens"] is None
    assert result["total_tokens"] is None
