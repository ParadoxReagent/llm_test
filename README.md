# LLM Model Comparison Tool

A Python tool to compare responses from multiple Large Language Models (LLMs) using the litellm API. Enter a prompt and see how different models respond side-by-side to evaluate which model works best for your use case.

## Features

- 🤖 Compare multiple LLM models simultaneously
- 💬 Interactive mode for testing multiple prompts
- 🎯 Single-prompt mode for quick comparisons
- 🔧 Customizable model selection
- 🌡️ Adjustable temperature settings
- ✨ Clean, formatted output for easy comparison

## Supported Models

Thanks to litellm, you can use models from many providers:

- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`, `gpt-4`, etc.
- **Anthropic**: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, etc.
- **Google**: `gemini/gemini-1.5-pro`, `gemini/gemini-1.5-flash`, etc.
- **And many more!** See [litellm providers](https://docs.litellm.ai/docs/providers)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd llm_test
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API keys:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Or export them directly:
```bash
export OPENAI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
export GEMINI_API_KEY="your_key_here"
```

## Usage

### Interactive Mode (Default)

Run the script without arguments to enter interactive mode:

```bash
python llm_compare.py
```

This allows you to enter multiple prompts and see comparisons in real-time.

### Single Prompt Mode

Compare models with a single prompt:

```bash
python llm_compare.py -p "Explain quantum computing in simple terms"
```

### Custom Models

Specify which models to compare:

```bash
python llm_compare.py -m gpt-4o claude-3-5-sonnet-20241022 gemini/gemini-1.5-flash -p "Write a haiku about coding"
```

### Adjust Temperature

Control the creativity/randomness of responses (0-1):

```bash
python llm_compare.py -p "Write a creative story" -t 0.9
```

### Full Command Reference

```bash
python llm_compare.py [-h] [-p PROMPT] [-m MODEL1 MODEL2 ...] [-t TEMPERATURE]

Options:
  -h, --help            Show help message
  -p, --prompt PROMPT   Prompt to send to all models
  -m, --models MODELS   Models to compare (default: gpt-4o-mini, gpt-3.5-turbo,
                        claude-3-5-sonnet-20241022, gemini/gemini-1.5-flash)
  -t, --temperature T   Temperature for responses (0-1, default: 0.7)
```

## Examples

**Compare creative writing:**
```bash
python llm_compare.py -p "Write a short poem about AI" -t 0.8
```

**Compare code generation:**
```bash
python llm_compare.py -p "Write a Python function to calculate Fibonacci numbers" -m gpt-4o claude-3-5-sonnet-20241022
```

**Compare explanations:**
```bash
python llm_compare.py -p "Explain neural networks to a 10-year-old"
```

## Output Format

The tool displays results in an easy-to-read format:

```
================================================================================
Prompt: Your prompt here
================================================================================

[1/3] Getting response from gpt-4o-mini... ✓
[2/3] Getting response from claude-3-5-sonnet-20241022... ✓
[3/3] Getting response from gemini/gemini-1.5-flash... ✓

================================================================================
RESULTS
================================================================================

────────────────────────────────────────────────────────────────────────────────
Model 1: gpt-4o-mini
────────────────────────────────────────────────────────────────────────────────

[Response from gpt-4o-mini]

────────────────────────────────────────────────────────────────────────────────
Model 2: claude-3-5-sonnet-20241022
────────────────────────────────────────────────────────────────────────────────

[Response from claude-3-5-sonnet-20241022]

...
```

## Tips

- Start with the default models to compare different providers
- Use lower temperature (0.1-0.3) for factual/technical responses
- Use higher temperature (0.7-0.9) for creative tasks
- In interactive mode, type `quit`, `exit`, or `q` to exit
- Make sure you have API keys for the models you want to test

## Troubleshooting

**"No API keys found"**: Make sure you've set the appropriate environment variables for the models you're using.

**Model errors**: Check that:
- Your API key is valid and has access to the model
- You're using the correct model identifier (see [litellm docs](https://docs.litellm.ai/docs/providers))
- You have sufficient credits/quota with the provider

## License

MIT License - feel free to use and modify as needed.
