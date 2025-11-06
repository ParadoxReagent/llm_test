"""
CLI interface for LLM Compare.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .analytics import ComparisonAnalytics
from .api_client import LLMAPIClient
from .config import Config
from .display import DisplayManager
from .export import ResultExporter
from .types import ModelResponse
from .validators import validate_prompt

# Import models from the old models.py file for backwards compatibility
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import models
except ImportError:
    # Fallback defaults if models.py doesn't exist
    class models:  # type: ignore
        MODELS = ["gpt-4o-mini", "claude-3-5-sonnet-20241022"]
        CREATIVE_MODELS = ["gpt-4o", "claude-3-5-sonnet-20241022"]
        FAST_MODELS = ["gpt-4o-mini", "gpt-3.5-turbo"]
        CODING_MODELS = ["gpt-4o", "claude-3-5-sonnet-20241022"]
        DEFAULT_TEMPERATURE = 0.7


async def compare_models_async(
    prompt: str,
    models_list: List[str],
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    stream: bool = False,
    config: Optional[Config] = None,
) -> List[ModelResponse]:
    """
    Compare models asynchronously.

    Args:
        prompt: User prompt
        models_list: List of models
        temperature: Temperature parameter
        system_prompt: Optional system prompt
        stream: Whether to stream
        config: Optional config object

    Returns:
        List of model responses
    """
    display = DisplayManager()

    # Use config values if provided
    if config:
        max_retries = config.max_retries
        retry_delay = config.retry_delay
        timeout = config.timeout
    else:
        max_retries = 3
        retry_delay = 1.0
        timeout = 120

    client = LLMAPIClient(
        max_retries=max_retries, retry_delay=retry_delay, timeout=timeout
    )

    display.print_header(prompt, system_prompt, len(models_list))

    # Get results
    results = await client.compare_models(
        prompt=prompt,
        models=models_list,
        temperature=temperature,
        system_prompt=system_prompt,
        stream=stream,
    )

    # Display progress for each completed model
    for i, result in enumerate(results, 1):
        if result["error"]:
            display.display_progress_update(
                i, len(models_list), result["model"], False, f"Error: {result['error']}"
            )
        else:
            response_time_str = (
                f"{result['response_time']:.2f}s" if result["response_time"] else "N/A"
            )
            tokens_str = (
                f"{result['total_tokens']} tokens" if result["total_tokens"] else "N/A"
            )
            display.display_progress_update(
                i,
                len(models_list),
                result["model"],
                True,
                f"({response_time_str}, {tokens_str})",
            )

    return results


async def interactive_mode_async(
    models_list: List[str],
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    config: Optional[Config] = None,
) -> None:
    """
    Run in interactive mode.

    Args:
        models_list: List of models
        temperature: Temperature parameter
        system_prompt: Optional system prompt
        config: Optional config object
    """
    display = DisplayManager()
    display.display_welcome(models_list, system_prompt)

    while True:
        try:
            prompt = input("\nPrompt: ").strip()

            if not prompt:
                continue

            if prompt.lower() in ["quit", "exit", "q"]:
                display.display_info("\nGoodbye!")
                break

            # Validate prompt
            try:
                validate_prompt(prompt, "prompt")
            except ValueError as e:
                display.display_error(str(e))
                continue

            results = await compare_models_async(
                prompt, models_list, temperature, system_prompt, config=config
            )
            display.display_results(results)

            # Show analytics
            analytics = ComparisonAnalytics(results)
            display.console.print(analytics.get_summary())

        except KeyboardInterrupt:
            display.display_info("\n\nGoodbye!")
            break
        except Exception as e:
            display.display_error(f"\n❌ Error: {e}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare responses from multiple LLM models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with default models
  llm-compare

  # Single prompt with default models
  llm-compare -p "Explain quantum computing"

  # Use a config file
  llm-compare --config config.yaml -p "Write a story"

  # Use a preset model list
  llm-compare --preset creative -p "Write a story"

  # Custom models
  llm-compare -m gpt-4o claude-3-5-sonnet-20241022 -p "Write a haiku"

  # Export results
  llm-compare -p "What is Python?" -o results.json

Configuration:
  - Edit models.py to customize default models
  - Create a config.yaml or config.json for advanced settings
  - All models use LITELLM_API_KEY environment variable
        """,
    )

    parser.add_argument(
        "-p", "--prompt", type=str, help="Prompt to send to all models"
    )

    parser.add_argument(
        "-m", "--models", nargs="+", help="Models to compare (overrides config)"
    )

    parser.add_argument(
        "--preset",
        type=str,
        choices=["creative", "fast", "coding"],
        help="Use a preset model list",
    )

    parser.add_argument(
        "-t", "--temperature", type=float, help="Temperature for responses (0-1)"
    )

    parser.add_argument(
        "-s", "--system-prompt", type=str, help="System prompt for all models"
    )

    parser.add_argument(
        "-o", "--output", type=str, help="Export results to file (json/csv/md)"
    )

    parser.add_argument(
        "--export-format",
        type=str,
        choices=["json", "csv", "markdown"],
        help="Export format (auto-detected from extension)",
    )

    parser.add_argument(
        "--config", type=str, help="Path to config file (YAML or JSON)"
    )

    parser.add_argument(
        "--create-config",
        type=str,
        help="Create an example config file at specified path",
    )

    parser.add_argument(
        "--stream", action="store_true", help="Stream responses (single model only)"
    )

    parser.add_argument(
        "--table", action="store_true", help="Display results in table format"
    )

    args = parser.parse_args()

    # Create example config if requested
    if args.create_config:
        Config.create_example_config(args.create_config)
        print(f"✅ Example config created at: {args.create_config}")
        return

    # Load config if provided
    config = None
    if args.config:
        try:
            config = Config(args.config)
        except Exception as e:
            print(f"❌ Error loading config file: {e}")
            sys.exit(1)

    # Determine which models to use
    if args.models:
        selected_models = args.models
    elif args.preset:
        preset_map = {
            "creative": models.CREATIVE_MODELS,
            "fast": models.FAST_MODELS,
            "coding": models.CODING_MODELS,
        }
        selected_models = preset_map[args.preset]
        print(f"Using {args.preset} preset models")
    elif config and config.models:
        selected_models = config.models
    else:
        selected_models = models.MODELS

    # Validate models list
    if not selected_models:
        print(
            "❌ Error: No models specified. Configure models in models.py, config file, or use -m"
        )
        sys.exit(1)

    # Determine temperature
    if args.temperature is not None:
        temperature = args.temperature
    elif config and config.temperature:
        temperature = config.temperature
    else:
        temperature = models.DEFAULT_TEMPERATURE

    # Validate temperature
    if not 0 <= temperature <= 1:
        print("❌ Error: Temperature must be between 0 and 1")
        sys.exit(1)

    # Check API key
    if not os.getenv("LITELLM_API_KEY"):
        print("❌ Error: LITELLM_API_KEY not found in environment variables.")
        print("   Set it with: export LITELLM_API_KEY='your_key_here'")
        print("   Or add it to a .env file")
        sys.exit(1)

    # Validate system prompt
    system_prompt = args.system_prompt
    if system_prompt:
        try:
            validate_prompt(system_prompt, "system_prompt")
        except ValueError as e:
            print(str(e))
            sys.exit(1)

    # Determine export format
    export_format = None
    if args.output:
        if args.export_format:
            export_format = args.export_format
        else:
            ext = args.output.split(".")[-1].lower()
            if ext == "json":
                export_format = "json"
            elif ext == "csv":
                export_format = "csv"
            elif ext in ["md", "markdown"]:
                export_format = "markdown"
            else:
                print(
                    f"⚠️  Warning: Unknown format '.{ext}', defaulting to JSON"
                )
                export_format = "json"

    # Run comparison
    display = DisplayManager()

    if args.prompt:
        # Single prompt mode
        results = asyncio.run(
            compare_models_async(
                args.prompt,
                selected_models,
                temperature,
                system_prompt,
                args.stream,
                config,
            )
        )

        # Display results
        if args.table:
            display.display_comparison_table(results)
        display.display_results(results)

        # Show analytics
        analytics = ComparisonAnalytics(results)
        display.console.print(analytics.get_summary())

        # Export if requested
        if args.output:
            try:
                ResultExporter.export_results(
                    results, args.prompt, export_format, args.output, system_prompt  # type: ignore
                )
                display.display_success(f"✅ Results exported to: {args.output}")
            except Exception as e:
                display.display_error(str(e))
    else:
        # Interactive mode
        if args.output:
            display.display_info(
                "⚠️  Warning: Export is only supported in single-prompt mode"
            )
        asyncio.run(
            interactive_mode_async(selected_models, temperature, system_prompt, config)
        )


if __name__ == "__main__":
    main()
