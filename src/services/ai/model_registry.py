"""
Available AI models for OpenRouter.
Verified active free models.
"""

FREE_MODELS = [

    # ۱. سریع‌ترین مدل (Nvidia Nano)
    "nvidia/nemotron-nano-9b-v2:free",
    
    # ۲. سریع و هوشمند
    "nvidia/nemotron-3-nano-30b-a3b:free",
    
    # ۳. مدل‌های قدرتمند گوگل
    "google/gemma-4-31b:free",
    "google/gemma-4-26b-a4b:free",
    
    # ۴. بسیار حرفه‌ای با حافظه ۱ میلیون توکن
    "nvidia/nemotron-3-super:free",
    "nvidia/nemotron-3-ultra:free",
    
    # ۵. تنسنت و پول‌ساید
    "tencent/hy3:free",
    "poolside/laguna-xs-2.1:free",
    
    # ۶. OpenAI (کندترین)
    "openai/gpt-oss-20b:free"

]


def get_models():
    """
    Return models priority list.
    """
    return FREE_MODELS