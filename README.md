# LLM Model Comparison Tool

A powerful Python tool to compare responses from multiple Large Language Models (LLMs) using a single litellm API key. Enter a prompt and see how different models respond side-by-side to evaluate which model works best for your use case.

## ✨ Features

### Core Features
- 🤖 Compare multiple LLM models simultaneously
- 🔑 Single API key for all models
- 💬 Interactive mode for testing multiple prompts
- 🎯 Single-prompt mode for quick comparisons
- 🔧 Easy model customization via `models.py` or config files
- 📋 Preset model lists for different use cases
- 🌡️ Adjustable temperature settings

### Advanced Features (v2.0+)
- ⚡ **Async/Await** - Lightning-fast parallel execution with asyncio
- 🔄 **Retry Logic** - Automatic retry with exponential backoff for transient failures
- 📊 **Comprehensive Analytics** - Detailed comparison statistics including fastest/slowest models, token efficiency, and success rates
- 💰 **Cost Tracking** - Real-time cost estimation per model with support for 25+ models
- 🎨 **Rich UI** - Beautiful terminal output with progress indicators, tables, and colored formatting
- 💾 **Export Results** - Save comparisons to JSON, CSV, or Markdown formats
- 🎭 **Custom System Prompts** - Set system prompts for specialized behavior
- ⚙️ **Config Files** - YAML/JSON configuration support for complex setups
- 🐳 **Docker Support** - Ready-to-use Docker containers and docker-compose
- 📡 **Streaming Support** - Stream responses in real-time (experimental)
- 🧪 **Modular Architecture** - Clean, maintainable, fully typed codebase

## 🚀 Quick Start

### Installation

#### Option 1: Package Installation (Recommended)
```bash
# Install as a package
pip install -e .

# Or with locked dependencies for production
pip install -r requirements-lock.txt
pip install -e .

# Run from anywhere
llm-compare -p "Explain quantum computing"
```

#### Option 2: Direct Installation
```bash
pip install -r requirements.txt
python -m llm_compare.cli -p "Explain quantum computing"
```

#### Option 3: Docker
```bash
# Build and run with docker-compose
docker-compose run llm-compare -p "Explain quantum computing"

# Or build manually
docker build -t llm-compare .
docker run -e LITELLM_API_KEY="your_key" llm-compare -p "Hello world"
```

### Setup

1. **Set your litellm API key:**
```bash
export LITELLM_API_KEY="your_key_here"
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your key
```

2. **Run your first comparison:**
```bash
llm-compare -p "Explain quantum computing"
```

## 📖 Usage

### Interactive Mode (Default)

Run without arguments to enter interactive mode:

```bash
llm-compare
```

This allows you to enter multiple prompts and see comparisons in real-time with analytics after each comparison.

### Single Prompt Mode

Compare models with a single prompt:

```bash
llm-compare -p "Explain quantum computing in simple terms"
```

### Using Configuration Files

Create and use configuration files for complex setups:

```bash
# Create an example config file
llm-compare --create-config config.yaml

# Edit config.yaml with your preferences

# Use the config file
llm-compare --config config.yaml -p "Your prompt"
```

Example `config.yaml`:
```yaml
models:
  - gpt-4o-mini
  - claude-3-5-sonnet-20241022
  - gemini/gemini-1.5-flash
temperature: 0.7
max_retries: 3
retry_delay: 1.0
timeout: 120
stream: false
```

### Using Preset Model Lists

Use predefined model lists from `models.py`:

```bash
# For creative writing
llm-compare --preset creative -p "Write a short story"

# For fast responses
llm-compare --preset fast -p "Quick question"

# For coding tasks
llm-compare --preset coding -p "Write a function to sort a list"
```

### Override Models from Command Line

Temporarily use different models:

```bash
llm-compare -m gpt-4o claude-3-5-sonnet-20241022 gemini/gemini-1.5-pro -p "Write a haiku"
```

### Export Results

Save comparison results to a file:

```bash
# Export to JSON (includes all metadata)
llm-compare -p "What is AI?" -o results.json

# Export to CSV (great for spreadsheets)
llm-compare -p "What is AI?" -o results.csv

# Export to Markdown (formatted report)
llm-compare -p "What is AI?" -o results.md
```

### View Results in Table Format

Display results in a compact table:

```bash
llm-compare -p "Explain ML" --table
```

### Streaming Mode (Experimental)

Stream responses in real-time:

```bash
llm-compare -p "Tell me a story" --stream
```

### Full Command Reference

```bash
llm-compare [-h] [-p PROMPT] [-m MODEL1 MODEL2 ...] [--preset PRESET]
            [-t TEMPERATURE] [-s SYSTEM_PROMPT] [-o OUTPUT]
            [--export-format FORMAT] [--config CONFIG]
            [--create-config PATH] [--stream] [--table]

Options:
  -h, --help                    Show help message
  -p, --prompt PROMPT           Prompt to send to all models
  -m, --models MODELS           Override models from config
  --preset PRESET               Use preset: creative, fast, or coding
  -t, --temperature T           Temperature (0-1)
  -s, --system-prompt PROMPT    Custom system prompt for all models
  -o, --output FILE             Export results to file
  --export-format FORMAT        Export format: json, csv, or markdown
  --config CONFIG               Path to config file (YAML or JSON)
  --create-config PATH          Create an example config file
  --stream                      Stream responses in real-time
  --table                       Display results in table format
```

## ⚙️ Configuration

### Method 1: models.py (Simple)

Edit `models.py` to customize default models and presets:

```python
MODELS = [
    "gpt-4o",
    "claude-3-5-sonnet-20241022",
    "gemini/gemini-1.5-pro"
]

CREATIVE_MODELS = [
    "gpt-4o",
    "claude-3-5-sonnet-20241022"
]

DEFAULT_TEMPERATURE = 0.7
```

### Method 2: Config Files (Advanced)

Use YAML or JSON config files for more control:

**config.yaml:**
```yaml
models:
  - gpt-4o-mini
  - claude-3-5-sonnet-20241022
temperature: 0.7
system_prompt: "You are a helpful assistant"
max_retries: 3
retry_delay: 1.0
timeout: 120
```

**config.json:**
```json
{
  "models": ["gpt-4o-mini", "claude-3-5-sonnet-20241022"],
  "temperature": 0.7,
  "max_retries": 3
}
```

## 📊 Analytics & Cost Tracking

Version 2.0 includes comprehensive analytics displayed after each comparison:

```
📊 Comparison Analytics:
────────────────────────────────────────────────────────────────────────────────
Success Rate: 100.0% (3/3 models)
Average Response Time: 1.55s
⚡ Fastest Model: gemini/gemini-1.5-flash (0.98s)
🐌 Slowest Model: claude-3-5-sonnet-20241022 (2.11s)
📝 Most Token Efficient: gpt-4o-mini (150 tokens)
💰 Total Cost: $0.000125
💵 Cheapest Model: gpt-4o-mini ($0.000045)
────────────────────────────────────────────────────────────────────────────────
```

### Cost Tracking

Automatic cost estimation for 25+ models including:
- OpenAI (GPT-4o, GPT-4o-mini, GPT-3.5-turbo, etc.)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus, etc.)
- Google (Gemini 1.5 Pro, Gemini 1.5 Flash, etc.)

Costs are displayed per request and in aggregate for easy comparison.

## 🐳 Docker Usage

### Using Docker Compose

```bash
# Interactive mode
docker-compose run llm-compare

# Single prompt
docker-compose run llm-compare -p "What is AI?"

# With config file
docker-compose run llm-compare --config /app/config/config.yaml -p "Hello"

# Export results (will be saved to ./exports/ directory)
docker-compose run llm-compare -p "Test" -o /app/exports/results.json
```

### Using Docker Directly

```bash
# Build image
docker build -t llm-compare .

# Run with environment variable
docker run -it -e LITELLM_API_KEY="your_key" llm-compare -p "Hello"

# Mount config directory
docker run -it -e LITELLM_API_KEY="your_key" \
  -v $(pwd)/config:/app/config \
  llm-compare --config /app/config/config.yaml -p "Test"
```

## 🔧 Development

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=llm_compare --cov-report=html

# Lint and format
ruff check .
ruff format .

# Type checking
mypy llm_compare
```

### Project Structure

```
llm_compare/
├── __init__.py          # Package initialization
├── analytics.py         # Comparison analytics and statistics
├── api_client.py        # Async API client with retry logic
├── cli.py              # CLI interface and main entry point
├── config.py           # Configuration file handling
├── cost_tracker.py     # Cost estimation for models
├── display.py          # Rich terminal UI and formatting
├── export.py           # Export functionality
├── types.py            # Type definitions
└── validators.py       # Input validation
```

## 🌐 Supported Models

The tool supports any models available through litellm, including:

### OpenAI
- `gpt-4o`, `gpt-4o-mini` (Recommended for most tasks)
- `gpt-4-turbo`, `gpt-4`
- `gpt-3.5-turbo`

### Anthropic
- `claude-3-5-sonnet-20241022` (Latest, recommended)
- `claude-3-opus-20240229` (Most capable)
- `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`

### Google
- `gemini/gemini-1.5-pro`, `gemini/gemini-1.5-flash`
- `gemini/gemini-pro`

### And many more!
See [litellm providers](https://docs.litellm.ai/docs/providers) for the full list.

All models use the same `LITELLM_API_KEY` environment variable.

## 📝 Example Output

```
================================================================================
Prompt: Write a haiku about coding
================================================================================

Querying 3 models in parallel...

[1/3] gpt-4o-mini: ✓ (1.23s, 245 tokens)
[2/3] claude-3-5-sonnet-20241022: ✓ (1.45s, 198 tokens)
[3/3] gemini/gemini-1.5-flash: ✓ (0.98s, 210 tokens)

================================================================================
RESULTS
================================================================================

────────────────────────────────────────────────────────────────────────────────
Model 1: gpt-4o-mini
📊 Time: 1.23s | Tokens: 245 (prompt: 15, completion: 230) | Cost: $0.000045
────────────────────────────────────────────────────────────────────────────────

Code flows like streams
Logic blooms in terminal
Debug finds the truth

────────────────────────────────────────────────────────────────────────────────
Model 2: claude-3-5-sonnet-20241022
📊 Time: 1.45s | Tokens: 198 (prompt: 15, completion: 183) | Cost: $0.000320
────────────────────────────────────────────────────────────────────────────────

Keys tap in rhythm
Functions dance through the darkness
Bugs flee from the light

📊 Comparison Analytics:
────────────────────────────────────────────────────────────────────────────────
Success Rate: 100.0% (3/3 models)
⚡ Fastest Model: gemini/gemini-1.5-flash (0.98s)
💵 Cheapest Model: gpt-4o-mini ($0.000045)
💰 Total Cost: $0.000502
────────────────────────────────────────────────────────────────────────────────
```

## 💡 Tips & Best Practices

- **Use config files** for complex setups with multiple model combinations
- Use lower temperature (0.1-0.3) for factual/technical responses
- Use higher temperature (0.7-0.9) for creative tasks
- **Check analytics** to find the best model for your use case (fastest, cheapest, most efficient)
- **Export results** to track model performance over time
- Use **system prompts** to make models behave as domain experts
- **Docker** is great for reproducible environments and CI/CD pipelines
- The **cost tracker** helps you optimize API spend

## 🔒 Security

- Input validation prevents injection attacks (null bytes, excessive length)
- Secrets are managed via environment variables (never committed to git)
- Docker containers run as non-root user for better security

## 🚨 Troubleshooting

**"LITELLM_API_KEY not found"**:
```bash
export LITELLM_API_KEY="your_key_here"
# Or add it to .env file
```

**Model errors**: Check that:
- Your API key is valid
- You're using the correct model identifier ([litellm docs](https://docs.litellm.ai/docs/providers))
- The model is available through your litellm service/proxy

**Import errors**:
```bash
pip install -r requirements.txt
# Or for locked versions:
pip install -r requirements-lock.txt
```

**Docker permission issues**:
```bash
# Add your user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

## 🤝 Contributing

Contributions are welcome! The codebase now follows a modular architecture:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run tests: `pytest`
5. Submit a pull request

## 📜 License

MIT License - feel free to use and modify as needed.

## 🔄 Version History

### v2.0.0 (Latest)
- ⚡ Async/await architecture with asyncio
- 🔄 Automatic retry with exponential backoff
- 📊 Comprehensive analytics and statistics
- 💰 Cost tracking for 25+ models
- 🎨 Rich terminal UI with progress indicators
- ⚙️ YAML/JSON configuration support
- 🐳 Docker and docker-compose support
- 📡 Streaming support (experimental)
- 🧪 Modular, fully typed codebase
- ✅ Comprehensive test suite

### v1.x
- Basic comparison functionality
- Parallel execution with ThreadPoolExecutor
- Export to JSON/CSV/Markdown
- Custom system prompts

## 📚 Additional Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Supported Model Providers](https://docs.litellm.ai/docs/providers)
- [Cost Calculator](https://openai.com/pricing)
