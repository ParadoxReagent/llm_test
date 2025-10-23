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
from typing import List, Dict
import argparse
import models  # Import model configurations


def get_model_response(model: str, prompt: str, temperature: float = 0.7) -> Dict[str, str]:
    """
    Get response from a specific model.

    Args:
        model: Model identifier
        prompt: User prompt
        temperature: Response temperature (0-1)

    Returns:
        Dictionary with model name and response
    """
    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return {
            "model": model,
            "response": response.choices[0].message.content,
            "error": None
        }
    except Exception as e:
        return {
            "model": model,
            "response": None,
            "error": str(e)
        }


def compare_models(prompt: str, models: List[str], temperature: float = 0.7) -> List[Dict[str, str]]:
    """
    Compare responses from multiple models.

    Args:
        prompt: User prompt
        models: List of model identifiers
        temperature: Response temperature

    Returns:
        List of response dictionaries
    """
    results = []

    print(f"\n{'='*80}")
    print(f"Prompt: {prompt}")
    print(f"{'='*80}\n")

    for i, model in enumerate(models, 1):
        print(f"[{i}/{len(models)}] Getting response from {model}...", end=" ", flush=True)
        result = get_model_response(model, prompt, temperature)
        results.append(result)

        if result["error"]:
            print(f"❌ Error: {result['error']}")
        else:
            print("✓")

    return results


def display_results(results: List[Dict[str, str]]):
    """
    Display comparison results in a formatted manner.

    Args:
        results: List of response dictionaries
    """
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}\n")

    for i, result in enumerate(results, 1):
        print(f"\n{'─'*80}")
        print(f"Model {i}: {result['model']}")
        print(f"{'─'*80}")

        if result["error"]:
            print(f"\n❌ Error: {result['error']}\n")
        else:
            print(f"\n{result['response']}\n")


def interactive_mode(models: List[str], temperature: float = 0.7):
    """
    Run in interactive mode, allowing multiple prompts.

    Args:
        models: List of model identifiers
        temperature: Response temperature
    """
    print("\n🤖 LLM Model Comparison Tool")
    print(f"Comparing models: {', '.join(models)}")
    print("\nEnter your prompts (or 'quit' to exit)\n")

    while True:
        try:
            prompt = input("\nPrompt: ").strip()

            if not prompt:
                continue

            if prompt.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            results = compare_models(prompt, models, temperature)
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

    # Determine temperature
    temperature = args.temperature if args.temperature is not None else models.DEFAULT_TEMPERATURE

    # Validate temperature
    if not 0 <= temperature <= 1:
        print("❌ Error: Temperature must be between 0 and 1")
        sys.exit(1)

    # Check for API key
    if not os.getenv("LITELLM_API_KEY"):
        print("⚠️  Warning: LITELLM_API_KEY not found in environment variables.")
        print("   Set LITELLM_API_KEY to your litellm API key.")
        print("   Example: export LITELLM_API_KEY='your_key_here'\n")

    # Run in single-prompt or interactive mode
    if args.prompt:
        results = compare_models(args.prompt, selected_models, temperature)
        display_results(results)
    else:
        interactive_mode(selected_models, temperature)


if __name__ == "__main__":
    main()
