#!/usr/bin/env python3
"""
LLM Model Comparison Tool
Compare responses from multiple LLM models using litellm
"""

import os
import sys
from litellm import completion
from typing import List, Dict
import argparse


# Default models to compare
DEFAULT_MODELS = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
    "claude-3-5-sonnet-20241022",
    "gemini/gemini-1.5-flash"
]


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
        description="Compare responses from multiple LLM models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with default models
  python llm_compare.py

  # Single prompt with default models
  python llm_compare.py -p "Explain quantum computing"

  # Custom models
  python llm_compare.py -m gpt-4o claude-3-5-sonnet-20241022 -p "Write a haiku"

  # Adjust temperature
  python llm_compare.py -p "Be creative" -t 0.9

Supported models include:
  - OpenAI: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
  - Anthropic: claude-3-5-sonnet-20241022, claude-3-opus-20240229
  - Google: gemini/gemini-1.5-pro, gemini/gemini-1.5-flash
  - And many more via litellm!
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
        default=DEFAULT_MODELS,
        help=f"Models to compare (default: {' '.join(DEFAULT_MODELS)})"
    )

    parser.add_argument(
        "-t", "--temperature",
        type=float,
        default=0.7,
        help="Temperature for model responses (0-1, default: 0.7)"
    )

    args = parser.parse_args()

    # Validate temperature
    if not 0 <= args.temperature <= 1:
        print("❌ Error: Temperature must be between 0 and 1")
        sys.exit(1)

    # Check for API key (litellm will use various env vars)
    if not any([
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("GEMINI_API_KEY"),
        os.getenv("LITELLM_API_KEY")
    ]):
        print("⚠️  Warning: No API keys found in environment variables.")
        print("   Set OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, or other relevant keys.")
        print("   See: https://docs.litellm.ai/docs/\n")

    # Run in single-prompt or interactive mode
    if args.prompt:
        results = compare_models(args.prompt, args.models, args.temperature)
        display_results(results)
    else:
        interactive_mode(args.models, args.temperature)


if __name__ == "__main__":
    main()
