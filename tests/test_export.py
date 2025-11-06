"""Tests for export module."""

from unittest.mock import patch

import pytest

from llm_compare.export import ResultExporter
from llm_compare.types import ModelResponse


@pytest.fixture
def mock_results():
    """Fixture for mock results data."""
    return [
        ModelResponse(
            model="model-1",
            response="Response from model 1",
            error=None,
            response_time=1.23,
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            estimated_cost=0.001,
        ),
        ModelResponse(
            model="model-2",
            response=None,
            error="API error",
            response_time=None,
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            estimated_cost=None,
        ),
    ]


def test_export_results_json(tmp_path, mock_results):
    """Test exporting results to JSON."""
    output_file = tmp_path / "results.json"
    ResultExporter.export_results(mock_results, "Test prompt", "json", str(output_file))

    assert output_file.exists()
    with open(output_file, "r") as f:
        data = f.read()
        assert '"prompt": "Test prompt"' in data
        assert '"model": "model-1"' in data
        assert '"response": "Response from model 1"' in data


def test_export_results_csv(tmp_path, mock_results):
    """Test exporting results to CSV."""
    output_file = tmp_path / "results.csv"
    ResultExporter.export_results(mock_results, "Test prompt", "csv", str(output_file))

    assert output_file.exists()
    with open(output_file, "r") as f:
        data = f.read()
        assert "Timestamp,Prompt,System Prompt,Model,Response,Response Time (s)" in data
        assert "model-1,Response from model 1,1.23" in data
        assert "model-2" in data


def test_export_results_markdown(tmp_path, mock_results):
    """Test exporting results to Markdown."""
    output_file = tmp_path / "results.md"
    prompt = "Summarize this for me"
    system_prompt = "Act like a pirate"
    ResultExporter.export_results(
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


def test_export_results_creates_directory(tmp_path, mock_results):
    """Test that export creates directory if it doesn't exist."""
    output_file = tmp_path / "subdir" / "results.json"
    ResultExporter.export_results(mock_results, "prompt", "json", str(output_file))

    assert output_file.exists()


def test_export_results_permission_error(mock_results):
    """Test handling of permission errors."""
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(PermissionError, match="Permission denied"):
            ResultExporter.export_results(
                mock_results, "prompt", "json", "/dev/null/test.json"
            )


def test_export_results_os_error(mock_results):
    """Test handling of OS errors."""
    with patch("builtins.open", side_effect=OSError("Disk full")):
        with pytest.raises(OSError, match="Disk full"):
            ResultExporter.export_results(
                mock_results, "prompt", "csv", "nonexistent/path/results.csv"
            )
