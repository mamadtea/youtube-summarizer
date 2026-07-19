import os
import json
import time
import re
import logging

from openai import OpenAI

from src.services.ai.model_registry import get_models

logger = logging.getLogger("youtube_summarizer")


class OpenRouterClient:
    """
    Reliable OpenRouter client

    Features:
    - Multiple model fallback
    - Retry system
    - JSON cleaning
    - Error handling
    """

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is missing")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

        # گرفتن مدل ها از registry
        self.models = get_models()
        self.max_retries = 3

    def summarize_text(self, prompt: str) -> str:
        """
        Used for map stage
        """
        return self._request(prompt)

    def summarize_json(self, system_prompt: str, user_prompt: str) -> dict:
        """
        Generate JSON summary
        """
        response = self._request(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        return self._parse_json(response)

    def _request(self, prompt: str, system_prompt: str = None) -> str:
        last_error = None

        for model in self.models:
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Trying model: {model}")

                    messages = []

                    if system_prompt:
                        messages.append({
                            "role": "system",
                            "content": system_prompt
                        })

                    messages.append({
                        "role": "user",
                        "content": prompt
                    })

                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.2,
                        max_tokens=3000,
                        timeout=90
                    )

                    if not response.choices:
                        raise Exception("No choices returned")

                    content = response.choices[0].message.content

                    if not content:
                        raise Exception("Empty AI response")

                    return content

                except Exception as e:
                    last_error = e
                    logger.error(f"Model failed: {model} | Attempt: {attempt + 1} | Error: {e}")
                    time.sleep(2 ** attempt)

        raise Exception(f"All AI models failed: {last_error}")

    def _parse_json(self, text: str) -> dict:
        """
        Extract valid JSON from AI response
        """
        if not text:
            return {"error": "Empty response"}

        # حالت مستقیم JSON
        try:
            return json.loads(text)
        except Exception:
            pass

        #