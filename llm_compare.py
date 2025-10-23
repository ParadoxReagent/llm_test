#!/usr/bin/env python3
"""
LLM Model Comparison Tool
Compare responses from multiple LLM models using litellm

All models use the same LITELLM_API_KEY from your environment.
Edit models.py to customize which models to compare.
"""

import os
import sys
from litellm import completion
from typing import List, Dict, Optional
import argparse
import models  # Import model configurations
import time
import json
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Security constants
MAX_PROMPT_LENGTH = 50000  # Maximum characters for a prompt
MAX_SYSTEM_PROMPT_LENGTH = 10000  # Maximum characters for system prompt


def validate_prompt(prompt: str, prompt_type: str = "prompt") -> bool:
    """
    Validate prompt input for security and sanity.

    Args:
        prompt: The prompt to validate
        prompt_type: Type of prompt ("prompt" or "system_prompt")

    Returns:
        True if valid

    Raises:
        ValueError: If prompt is invalid
    """
    if not prompt:
        raise ValueError(f"❌ Error: {prompt_type.capitalize()} cannot be empty")

    # Check length based on prompt type
    max_length = MAX_SYSTEM_PROMPT_LENGTH if prompt_type == "system_prompt" else MAX_PROMPT_LENGTH
    if len(prompt) > max_length:
        raise ValueError(
            f"❌ Error: {prompt_type.capitalize()} is too long ({len(prompt)} characters). "
            f"Maximum allowed: {max_length} characters"
        )

    # Strip any null bytes (potential injection attack)
    if '\0' in prompt:
        raise ValueError(f"❌ Error: {prompt_type.capitalize()} contains invalid null bytes")

    return True


def get_model_response(model: str, prompt: str, temperature: float = 0.7, system_prompt: Optional[str] = None) -> Dict[str, str]:
    """
    Get response from a specific model with timing and token counting.

    Args:
        model: Model identifier
        prompt: User prompt
        temperature: Response temperature (0-1)
        system_prompt: Optional system prompt to prepend

    Returns:
        Dictionary with model name, response, timing, and token usage
    """
    try:
        start_time = time.time()

        # Build messages list
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = completion(
            model=model,
            messages=messages,
            temperature=temperature
        )

        end_time = time.time()
        response_time = end_time - start_time

        # Extract token usage if available
        usage = response.usage if hasattr(response, 'usage') else None
        prompt_tokens = usage.prompt_tokens if usage else None
        completion_tokens = usage.completion_tokens if usage else None
        total_tokens = usage.total_tokens if usage else None

        return {
            "model": model,
            "response": response.choices[0].message.content,
            "error": None,
            "response_time": response_time,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    except Exception as e:
        return {
            "model": model,
            "response": None,
            "error": str(e),
            "response_time": None,
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None
        }


def compare_models(prompt: str, models: List[str], temperature: float = 0.7, system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Compare responses from multiple models in parallel.

    Args:
        prompt: User prompt
        models: List of model identifiers
        temperature: Response temperature
        system_prompt: Optional system prompt for all models

    Returns:
        List of response dictionaries
    """
    # Validate inputs
    try:
        validate_prompt(prompt, "prompt")
        if system_prompt:
            validate_prompt(system_prompt, "system_prompt")
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    print(f"\n{'='*80}")
    print(f"Prompt: {prompt}")
    if system_prompt:
        print(f"System Prompt: {system_prompt}")
    print(f"{'='*80}\n")

    results = [None] * len(models)  # Pre-allocate to maintain order
    completed_count = 0

    print(f"Querying {len(models)} models in parallel...\n")

    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(get_model_response, model, prompt, temperature, system_prompt): i
            for i, model in enumerate(models)
        }

        # Process results as they complete
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            model = models[index]
            completed_count += 1

            try:
                result = future.result()
                results[index] = result

                if result["error"]:
                    print(f"[{completed_count}/{len(models)}] {model}: ❌ Error: {result['error']}")
                else:
                    response_time_str = f"{result['response_time']:.2f}s" if result['response_time'] else "N/A"
                    tokens_str = f"{result['total_tokens']} tokens" if result['total_tokens'] else "N/A"
                    print(f"[{completed_count}/{len(models)}] {model}: ✓ ({response_time_str}, {tokens_str})")
            except Exception as e:
                results[index] = {
                    "model": model,
                    "response": None,
                    "error": str(e),
                    "response_time": None,
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "total_tokens": None
                }
                print(f"[{completed_count}/{len(models)}] {model}: ❌ Exception: {str(e)}")

    return results


def display_results(results: List[Dict[str, str]]):
    """
    Display comparison results in a formatted manner with performance metrics.

    Args:
        results: List of response dictionaries
    """
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}\n")

    for i, result in enumerate(results, 1):
        print(f"\n{'─'*80}")
        print(f"Model {i}: {result['model']}")

        # Display performance metrics
        metrics = []
        if result.get("response_time") is not None:
            metrics.append(f"Time: {result['response_time']:.2f}s")
        if result.get("total_tokens") is not None:
            metrics.append(f"Tokens: {result['total_tokens']} (prompt: {result.get('prompt_tokens', 'N/A')}, completion: {result.get('completion_tokens', 'N/A')})")

        if metrics:
            print(f"📊 {' | '.join(metrics)}")
        print(f"{'─'*80}")

        if result["error"]:
            print(f"\n❌ Error: {result['error']}\n")
        else:
            print(f"\n{result['response']}\n")


def export_results(results: List[Dict[str, str]], prompt: str, format: str, output_file: str, system_prompt: Optional[str] = None):
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
            export_data = {
                "timestamp": timestamp,
                "prompt": prompt,
                "system_prompt": system_prompt,
                "results": results
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

        elif format == "csv":
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Prompt", "System Prompt", "Model", "Response", "Response Time (s)", "Prompt Tokens", "Completion Tokens", "Total Tokens", "Error"])

                for result in results:
                    writer.writerow([
                        timestamp,
                        prompt,
                        system_prompt or "",
                        result["model"],
                        result["response"] or "",
                        result.get("response_time", ""),
                        result.get("prompt_tokens", ""),
                        result.get("completion_tokens", ""),
                        result.get("total_tokens", ""),
                        result.get("error", "")
                    ])

        elif format == "markdown":
            with open(output_file, 'w', encoding='utf-8') as f:
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
                        f.write(f"**Token Usage:** {result['total_tokens']} total (prompt: {result.get('prompt_tokens', 'N/A')}, completion: {result.get('completion_tokens', 'N/A')})\n\n")

                    if result["error"]:
                        f.write(f"**Error:** {result['error']}\n\n")
                    else:
                        f.write(f"**Response:**\n\n{result['response']}\n\n")

                    f.write(f"---\n\n")

        print(f"✅ Results exported to: {output_file}")

    except PermissionError:
        print(f"❌ Error: Permission denied when writing to {output_file}")
        print("   Check that you have write permissions for this location.")
    except OSError as e:
        print(f"❌ Error: Failed to write to {output_file}: {e}")
        print("   Check that the path is valid and the disk has space.")
    except Exception as e:
        print(f"❌ Error: Unexpected error while exporting results: {e}")


def interactive_mode(models: List[str], temperature: float = 0.7, system_prompt: Optional[str] = None):
    """
    Run in interactive mode, allowing multiple prompts.

    Args:
        models: List of model identifiers
        temperature: Response temperature
        system_prompt: Optional system prompt for all interactions
    """
    print("\n🤖 LLM Model Comparison Tool")
    print(f"Comparing models: {', '.join(models)}")
    if system_prompt:
        print(f"System prompt: {system_prompt}")
    print("\nEnter your prompts (or 'quit' to exit)\n")

    while True:
        try:
            prompt = input("\nPrompt: ").strip()

            if not prompt:
                continue

            if prompt.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            # Validate prompt before processing
            try:
                validate_prompt(prompt, "prompt")
            except ValueError as e:
                print(str(e))
                continue

            results = compare_models(prompt, models, temperature, system_prompt)
            display_results(results)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare responses from multiple LLM models using a single litellm API key",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with default models (from models.py)
  python llm_compare.py

  # Single prompt with default models
  python llm_compare.py -p "Explain quantum computing"

  # Use a preset model list
  python llm_compare.py --preset creative -p "Write a story"
  python llm_compare.py --preset fast -p "Quick question"
  python llm_compare.py --preset coding -p "Write a function"

  # Custom models (override models.py)
  python llm_compare.py -m gpt-4o claude-3-5-sonnet-20241022 -p "Write a haiku"

  # Adjust temperature
  python llm_compare.py -p "Be creative" -t 0.9

  # Use a custom system prompt
  python llm_compare.py -p "Explain AI" -s "You are a helpful teacher"

  # Export results to file (auto-detects format from extension)
  python llm_compare.py -p "What is Python?" -o results.json
  python llm_compare.py -p "What is Python?" -o results.csv
  python llm_compare.py -p "What is Python?" -o results.md

Configuration:
  - Edit models.py to customize default models and presets
  - All models use LITELLM_API_KEY environment variable
  - Supports any models available through litellm
        """
    )

    parser.add_argument(
        "-p", "--prompt",
        type=str,
        help="Prompt to send to all models (if not provided, runs in interactive mode)"
    )

    parser.add_argument(
        "-m", "--models",
        nargs="+",
        help="Models to compare (overrides default from models.py)"
    )

    parser.add_argument(
        "--preset",
        type=str,
        choices=["creative", "fast", "coding"],
        help="Use a preset model list from models.py (creative, fast, or coding)"
    )

    parser.add_argument(
        "-t", "--temperature",
        type=float,
        help=f"Temperature for model responses (0-1, default: {models.DEFAULT_TEMPERATURE})"
    )

    parser.add_argument(
        "-s", "--system-prompt",
        type=str,
        help="System prompt to use for all models"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Export results to file (e.g., results.json, results.csv, results.md)"
    )

    parser.add_argument(
        "--export-format",
        type=str,
        choices=["json", "csv", "markdown"],
        help="Export format (auto-detected from --output extension if not specified)"
    )

    args = parser.parse_args()

    # Determine which models to use
    if args.models:
        selected_models = args.models
    elif args.preset:
        preset_map = {
            "creative": models.CREATIVE_MODELS,
            "fast": models.FAST_MODELS,
            "coding": models.CODING_MODELS
        }
        selected_models = preset_map[args.preset]
        print(f"Using {args.preset} preset models")
    else:
        selected_models = models.MODELS

    # Validate models list is not empty
    if not selected_models:
        print("❌ Error: No models specified. Please configure models in models.py or use -m/--models")
        sys.exit(1)

    # Determine temperature
    temperature = args.temperature if args.temperature is not None else models.DEFAULT_TEMPERATURE

    # Validate temperature
    if not 0 <= temperature <= 1:
        print("❌ Error: Temperature must be between 0 and 1")
        sys.exit(1)

    # Check for API key (required)
    if not os.getenv("LITELLM_API_KEY"):
        print("❌ Error: LITELLM_API_KEY not found in environment variables.")
        print("   Set LITELLM_API_KEY to your litellm API key.")
        print("   Example: export LITELLM_API_KEY='your_key_here'")
        print("   Or add it to a .env file in the project directory")
        sys.exit(1)

    # Validate system prompt if provided
    if args.system_prompt:
        try:
            validate_prompt(args.system_prompt, "system_prompt")
        except ValueError as e:
            print(str(e))
            sys.exit(1)

    # Determine export format if output file is specified
    export_format = None
    if args.output:
        if args.export_format:
            export_format = args.export_format
        else:
            # Auto-detect from file extension
            ext = args.output.split('.')[-1].lower()
            if ext == 'json':
                export_format = 'json'
            elif ext == 'csv':
                export_format = 'csv'
            elif ext in ['md', 'markdown']:
                export_format = 'markdown'
            else:
                print(f"⚠️  Warning: Could not determine format from extension '.{ext}', defaulting to JSON")
                export_format = 'json'

    # Run in single-prompt or interactive mode
    if args.prompt:
        results = compare_models(args.prompt, selected_models, temperature, args.system_prompt)
        display_results(results)

        # Export if requested
        if args.output:
            export_results(results, args.prompt, export_format, args.output, args.system_prompt)
    else:
        if args.output:
            print("⚠️  Warning: Export (-o/--output) is only supported in single-prompt mode, not interactive mode")
        interactive_mode(selected_models, temperature, args.system_prompt)


if __name__ == "__main__":
    main()
