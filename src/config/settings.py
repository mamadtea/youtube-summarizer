import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

DEBUG = os.getenv("DEBUG", "True") == "True"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")