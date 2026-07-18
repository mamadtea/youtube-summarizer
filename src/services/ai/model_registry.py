"""
Available AI models for OpenRouter.

Models can change over time.
Keep fallback order here.
"""


FREE_MODELS = [

    # Fast general models

    "openai/gpt-oss-20b:free",


    "google/gemma-3-27b-it:free",


    "meta-llama/llama-3.3-70b-instruct:free",


    "qwen/qwen3-30b-a3b:free"

]




def get_models():

    """
    Return models priority list.
    """

    return FREE_MODELS