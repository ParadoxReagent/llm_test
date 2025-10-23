"""
Model Configuration File

Edit this file to customize which LLM models to compare.
All models will use the same LITELLM_API_KEY from your environment.

Add or remove models from the MODELS list below.
"""

# List of models to compare
# Edit this list to add/remove models you want to test
MODELS = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
    "claude-3-5-sonnet-20241022",
    "gemini/gemini-1.5-flash"
]

# You can also create custom model lists for different use cases:

# For creative tasks:
CREATIVE_MODELS = [
    "gpt-4o",
    "claude-3-5-sonnet-20241022",
    "gemini/gemini-1.5-pro"
]

# For fast/cheap comparisons:
FAST_MODELS = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
    "gemini/gemini-1.5-flash"
]

# For coding tasks:
CODING_MODELS = [
    "gpt-4o",
    "claude-3-5-sonnet-20241022"
]

# Default temperature setting
DEFAULT_TEMPERATURE = 0.7
