"""
AI models used by the YouTube summarizer.
"""

FREE_MODELS = [
    "openrouter/free",
]


def get_models() -> list[str]:
    """Return the AI model priority list."""
    return FREE_MODELS