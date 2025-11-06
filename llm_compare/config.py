"""
Configuration file handling for LLM Compare.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class Config:
    """Configuration manager for LLM Compare."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Optional path to config file (YAML or JSON)
        """
        self.models: List[str] = []
        self.temperature: float = 0.7
        self.system_prompt: Optional[str] = None
        self.max_retries: int = 3
        self.retry_delay: float = 1.0
        self.timeout: int = 120
        self.stream: bool = False

        # Load from file if provided
        if config_path:
            self.load_from_file(config_path)

    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a YAML or JSON file.

        Args:
            config_path: Path to config file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            if path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            elif path.suffix == ".json":
                data = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported config file format: {path.suffix}. Use .yaml, .yml, or .json"
                )

        self._parse_config(data)

    def _parse_config(self, data: Dict[str, Any]) -> None:
        """
        Parse configuration data.

        Args:
            data: Configuration dictionary
        """
        if "models" in data:
            self.models = data["models"]
        if "temperature" in data:
            self.temperature = float(data["temperature"])
        if "system_prompt" in data:
            self.system_prompt = data["system_prompt"]
        if "max_retries" in data:
            self.max_retries = int(data["max_retries"])
        if "retry_delay" in data:
            self.retry_delay = float(data["retry_delay"])
        if "timeout" in data:
            self.timeout = int(data["timeout"])
        if "stream" in data:
            self.stream = bool(data["stream"])

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration dictionary
        """
        return {
            "models": self.models,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout,
            "stream": self.stream,
        }

    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to a file.

        Args:
            config_path: Path to save config file
        """
        path = Path(config_path)
        data = self.to_dict()

        with open(path, "w", encoding="utf-8") as f:
            if path.suffix in [".yaml", ".yml"]:
                yaml.safe_dump(data, f, default_flow_style=False)
            elif path.suffix == ".json":
                json.dump(data, f, indent=2)
            else:
                raise ValueError(
                    f"Unsupported config file format: {path.suffix}. Use .yaml, .yml, or .json"
                )

    @classmethod
    def create_example_config(cls, config_path: str) -> None:
        """
        Create an example configuration file.

        Args:
            config_path: Path to create config file
        """
        example_config = cls()
        example_config.models = [
            "gpt-4o-mini",
            "claude-3-5-sonnet-20241022",
            "gemini/gemini-1.5-flash",
        ]
        example_config.temperature = 0.7
        example_config.system_prompt = None
        example_config.max_retries = 3
        example_config.retry_delay = 1.0
        example_config.timeout = 120
        example_config.stream = False

        example_config.save_to_file(config_path)
