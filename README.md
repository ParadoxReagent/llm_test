# LLM Model Comparison Tool

A Python tool to compare responses from multiple Large Language Models (LLMs) using a single litellm API key. Enter a prompt and see how different models respond side-by-side to evaluate which model works best for your use case.

## Features

- 🤖 Compare multiple LLM models simultaneously
- 🔑 Single API key for all models
- 💬 Interactive mode for testing multiple prompts
- 🎯 Single-prompt mode for quick comparisons
- 🔧 Easy model customization via `models.py`
- 📋 Preset model lists for different use cases
- 🌡️ Adjustable temperature settings
- ✨ Clean, formatted output for easy comparison

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set your litellm API key:**
```bash
export LITELLM_API_KEY="your_key_here"
```

3. **Run the comparison:**
```bash
python llm_compare.py -p "Explain quantum computing"
```

## Customizing Models

Edit `models.py` to change which models to compare. This is the easiest way to customize your experience!

```python
# In models.py, just edit this list:
MODELS = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
    "claude-3-5-sonnet-20241022",
    "gemini/gemini-1.5-flash"
]
```

You can add any models supported by litellm. The file also includes preset lists for different use cases:
- `CREATIVE_MODELS` - Best for creative writing
- `FAST_MODELS` - Fast and cost-effective models
- `CODING_MODELS` - Optimized for code generation

## Usage

### Interactive Mode (Default)

Run without arguments to enter interactive mode:

```bash
python llm_compare.py
```

This allows you to enter multiple prompts and see comparisons in real-time.

### Single Prompt Mode

Compare models with a single prompt:

```bash
python llm_compare.py -p "Explain quantum computing in simple terms"
```

### Using Preset Model Lists

Use predefined model lists from `models.py`:

```bash
# For creative writing
python llm_compare.py --preset creative -p "Write a short story"

# For fast responses
python llm_compare.py --preset fast -p "Quick question"

# For coding tasks
python llm_compare.py --preset coding -p "Write a function to sort a list"
```

### Override Models from Command Line

Temporarily use different models without editing `models.py`:

```bash
python llm_compare.py -m gpt-4o claude-3-5-sonnet-20241022 -p "Write a haiku"
```

### Adjust Temperature

Control the creativity/randomness of responses (0-1):

```bash
python llm_compare.py -p "Write a creative story" -t 0.9
```

### Full Command Reference

```bash
python llm_compare.py [-h] [-p PROMPT] [-m MODEL1 MODEL2 ...] [--preset PRESET] [-t TEMPERATURE]

Options:
  -h, --help              Show help message
  -p, --prompt PROMPT     Prompt to send to all models
  -m, --models MODELS     Override models from models.py
  --preset PRESET         Use preset: creative, fast, or coding
  -t, --temperature T     Temperature (0-1, default from models.py)
```

## Configuration Files

### `models.py` - Model Configuration

This is your main configuration file. Edit it to:
- Change default models
- Create custom preset lists
- Adjust default temperature

Example:
```python
MODELS = [
    "gpt-4o",
    "claude-3-5-sonnet-20241022",
    "gemini/gemini-1.5-pro"
]

DEFAULT_TEMPERATURE = 0.7
```

### `.env` - API Key

Store your litellm API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

Or set it directly:
```bash
export LITELLM_API_KEY="your_key_here"
```

## Supported Models

The tool supports any models available through litellm, including:

- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`, `gpt-4`, etc.
- **Anthropic**: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, etc.
- **Google**: `gemini/gemini-1.5-pro`, `gemini/gemini-1.5-flash`, etc.
- **And many more!** See [litellm providers](https://docs.litellm.ai/docs/providers)

All models use the same `LITELLM_API_KEY` environment variable.

## Example Output

```
================================================================================
Prompt: Write a haiku about coding
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

Code flows like streams
Logic blooms in terminal
Debug finds the truth

────────────────────────────────────────────────────────────────────────────────
Model 2: claude-3-5-sonnet-20241022
────────────────────────────────────────────────────────────────────────────────

Keys tap in rhythm
Functions dance through the darkness
Bugs flee from the light

...
```

## Tips

- **Edit `models.py` first** - This is the easiest way to customize your setup
- Use lower temperature (0.1-0.3) for factual/technical responses
- Use higher temperature (0.7-0.9) for creative tasks
- In interactive mode, type `quit`, `exit`, or `q` to exit
- Use `--preset` for quick access to common model combinations

## Troubleshooting

**"LITELLM_API_KEY not found"**: Make sure you've set the environment variable:
```bash
export LITELLM_API_KEY="your_key_here"
```

**Model errors**: Check that:
- Your API key is valid
- You're using the correct model identifier (see [litellm docs](https://docs.litellm.ai/docs/providers))
- The model is available through your litellm service/proxy

**Import errors**: Make sure you've installed the requirements:
```bash
pip install -r requirements.txt
```

## License

MIT License - feel free to use and modify as needed.
