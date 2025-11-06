"""
Export functionality for comparison results.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .types import ModelResponse


class ResultExporter:
    """Handle exporting comparison results to various formats."""

    @staticmethod
    def export_results(
        results: List[ModelResponse],
        prompt: str,
        format: str,
        output_file: str,
        system_prompt: Optional[str] = None,
    ) -> None:
        """
        Export comparison results to a file.

        Args:
            results: List of response dictionaries
            prompt: The original prompt
            format: Export format (json, csv, or markdown)
            output_file: Output file path
            system_prompt: Optional system prompt used
        """
        try:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().isoformat()

            if format == "json":
                ResultExporter._export_json(
                    results, prompt, output_file, timestamp, system_prompt
                )
            elif format == "csv":
                ResultExporter._export_csv(
                    results, prompt, output_file, timestamp, system_prompt
                )
            elif format == "markdown":
                ResultExporter._export_markdown(
                    results, prompt, output_file, timestamp, system_prompt
                )

        except PermissionError:
            raise PermissionError(
                f"❌ Error: Permission denied when writing to {output_file}\n"
                "   Check that you have write permissions for this location."
            )
        except OSError as e:
            raise OSError(
                f"❌ Error: Failed to write to {output_file}: {e}\n"
                "   Check that the path is valid and the disk has space."
            )
        except Exception as e:
            raise Exception(f"❌ Error: Unexpected error while exporting results: {e}")

    @staticmethod
    def _export_json(
        results: List[ModelResponse],
        prompt: str,
        output_file: str,
        timestamp: str,
        system_prompt: Optional[str] = None,
    ) -> None:
        """Export results to JSON format."""
        export_data = {
            "timestamp": timestamp,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "results": results,
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _export_csv(
        results: List[ModelResponse],
        prompt: str,
        output_file: str,
        timestamp: str,
        system_prompt: Optional[str] = None,
    ) -> None:
        """Export results to CSV format."""
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Timestamp",
                    "Prompt",
                    "System Prompt",
                    "Model",
                    "Response",
                    "Response Time (s)",
                    "Prompt Tokens",
                    "Completion Tokens",
                    "Total Tokens",
                    "Estimated Cost (USD)",
                    "Error",
                ]
            )

            for result in results:
                writer.writerow(
                    [
                        timestamp,
                        prompt,
                        system_prompt or "",
                        result["model"],
                        result["response"] or "",
                        result.get("response_time", ""),
                        result.get("prompt_tokens", ""),
                        result.get("completion_tokens", ""),
                        result.get("total_tokens", ""),
                        result.get("estimated_cost", ""),
                        result.get("error", ""),
                    ]
                )

    @staticmethod
    def _export_markdown(
        results: List[ModelResponse],
        prompt: str,
        output_file: str,
        timestamp: str,
        system_prompt: Optional[str] = None,
    ) -> None:
        """Export results to Markdown format."""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# LLM Model Comparison Results\n\n")
            f.write(f"**Timestamp:** {timestamp}\n\n")
            f.write(f"**Prompt:** {prompt}\n\n")
            if system_prompt:
                f.write(f"**System Prompt:** {system_prompt}\n\n")
            f.write(f"---\n\n")

            for i, result in enumerate(results, 1):
                f.write(f"## Model {i}: {result['model']}\n\n")

                # Performance metrics
                if result.get("response_time") is not None:
                    f.write(f"**Response Time:** {result['response_time']:.2f}s\n\n")
                if result.get("total_tokens") is not None:
                    f.write(
                        f"**Token Usage:** {result['total_tokens']} total "
                        f"(prompt: {result.get('prompt_tokens', 'N/A')}, "
                        f"completion: {result.get('completion_tokens', 'N/A')})\n\n"
                    )
                if result.get("estimated_cost") is not None:
                    f.write(f"**Estimated Cost:** ${result['estimated_cost']:.6f}\n\n")

                if result["error"]:
                    f.write(f"**Error:** {result['error']}\n\n")
                else:
                    f.write(f"**Response:**\n\n{result['response']}\n\n")

                f.write(f"---\n\n")
