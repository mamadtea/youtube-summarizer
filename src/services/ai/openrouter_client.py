import os
import json
import time
import re
import logging

from openai import OpenAI

from src.services.ai.model_registry import get_models

logger = logging.getLogger("youtube_summarizer")


class OpenRouterClient:
    """Reliable OpenRouter client with multiple model fallback and JSON cleaning."""

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is missing")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.models = get_models()
        self.max_retries = 1 # فقط ۱ بار تلاش برای هر مدل

    def summarize_json(self, system_prompt: str, user_prompt: str) -> dict:
        """Generate JSON summary using OpenRouter API."""
        response = self._request(prompt=user_prompt, system_prompt=system_prompt)
        return self._parse_json(response)

    def _request(self, prompt: str, system_prompt: str = None) -> str:
        """Try fetching response from available models with retry mechanism."""
        last_error = None
        
        for model in self.models:
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Trying model: {model} (Attempt {attempt + 1})")
                    
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})
                    
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.2,
                        max_tokens=1500,
                        timeout=45.0
                    )
                    
                    if not response.choices:
                        raise Exception("No choices returned")
                        
                    content = response.choices[0].message.content
                    
                    if not content:
                        raise Exception("Empty AI response")
                        
                    logger.info(f"Model {model} responded successfully.")
                    return content
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"Model {model} failed: {str(e)[:100]}")
                    
                    # اگر خطا 400 یا 404 یا تایم‌اوت یا جواب خالی بود، مستقیم بریم مدل بعدی
                    error_str = str(e)
                    if ("400" in error_str or "404" in error_str or 
                        "timeout" in error_str.lower() or "Empty AI response" in error_str):
                        break
                        
                    time.sleep(2 ** attempt)
                    
        raise Exception(f"All AI models failed: {last_error}")

    def _parse_json(self, text: str) -> dict:
        """Extract and clean valid JSON from AI response."""
        if not text:
            return {"error": "Empty response"}
            
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        cleaned = re.sub(r"```json|```", "", text).strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
                
        return {"error": "Invalid JSON", "raw": text}