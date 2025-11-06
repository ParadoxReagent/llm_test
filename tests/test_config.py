"""Tests for config module."""

import json
from pathlib import Path

import pytest
import yaml

from llm_compare.config import Config


def test_config_defaults():
    """Test default configuration values."""
    config = Config()
    assert config.models == []
    assert config.temperature == 0.7
    assert config.system_prompt is None
    assert config.max_retries == 3
    assert config.retry_delay == 1.0
    assert config.timeout == 120
    assert config.stream is False


def test_config_load_yaml(tmp_path):
    """Test loading configuration from YAML file."""
    config_data = {
        "models": ["gpt-4o", "claude-3-5-sonnet-20241022"],
        "temperature": 0.9,
        "system_prompt": "You are a helpful assistant",
        "max_retries": 5,
        "retry_delay": 2.0,
        "timeout": 180,
        "stream": True,
    }

    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.safe_dump(config_data, f)

    config = Config(str(config_file))
    assert config.models == ["gpt-4o", "claude-3-5-sonnet-20241022"]
    assert config.temperature == 0.9
    assert config.system_prompt == "You are a helpful assistant"
    assert config.max_retries == 5
    assert config.retry_delay == 2.0
    assert config.timeout == 180
    assert config.stream is True


def test_config_load_json(tmp_path):
    """Test loading configuration from JSON file."""
    config_data = {
        "models": ["gpt-4o-mini"],
        "temperature": 0.5,
        "system_prompt": None,
        "max_retries": 2,
        "retry_delay": 1.5,
        "timeout": 90,
        "stream": False,
    }

    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    config = Config(str(config_file))
    assert config.models == ["gpt-4o-mini"]
    assert config.temperature == 0.5
    assert config.system_prompt is None
    assert config.max_retries == 2
    assert config.retry_delay == 1.5
    assert config.timeout == 90
    assert config.stream is False


def test_config_load_nonexistent_file():
    """Test loading configuration from nonexistent file."""
    with pytest.raises(FileNotFoundError):
        Config("/nonexistent/config.yaml")


def test_config_load_invalid_format(tmp_path):
    """Test loading configuration from invalid format."""
    config_file = tmp_path / "config.txt"
    config_file.write_text("invalid config")

    with pytest.raises(ValueError, match="Unsupported config file format"):
        Config(str(config_file))


def test_config_to_dict():
    """Test converting configuration to dictionary."""
    config = Config()
    config.models = ["gpt-4o"]
    config.temperature = 0.8

    config_dict = config.to_dict()
    assert config_dict["models"] == ["gpt-4o"]
    assert config_dict["temperature"] == 0.8
    assert config_dict["system_prompt"] is None


def test_config_save_yaml(tmp_path):
    """Test saving configuration to YAML file."""
    config = Config()
    config.models = ["gpt-4o", "claude-3-5-sonnet-20241022"]
    config.temperature = 0.9

    config_file = tmp_path / "config.yaml"
    config.save_to_file(str(config_file))

    # Load and verify
    with open(config_file, "r") as f:
        loaded_data = yaml.safe_load(f)

    assert loaded_data["models"] == ["gpt-4o", "claude-3-5-sonnet-20241022"]
    assert loaded_data["temperature"] == 0.9


def test_config_save_json(tmp_path):
    """Test saving configuration to JSON file."""
    config = Config()
    config.models = ["gpt-4o-mini"]
    config.temperature = 0.5

    config_file = tmp_path / "config.json"
    config.save_to_file(str(config_file))

    # Load and verify
    with open(config_file, "r") as f:
        loaded_data = json.load(f)

    assert loaded_data["models"] == ["gpt-4o-mini"]
    assert loaded_data["temperature"] == 0.5


def test_config_create_example(tmp_path):
    """Test creating example configuration."""
    config_file = tmp_path / "example.yaml"
    Config.create_example_config(str(config_file))

    assert config_file.exists()

    # Load and verify structure
    with open(config_file, "r") as f:
        loaded_data = yaml.safe_load(f)

    assert "models" in loaded_data
    assert "temperature" in loaded_data
    assert loaded_data["temperature"] == 0.7
