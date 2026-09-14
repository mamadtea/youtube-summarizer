
import json
import logging
import os
import re
import time

from dotenv import load_dotenv
from openai import OpenAI

from src.services.ai.model_registry import get_models

load_dotenv()

logger = logging.getLogger("youtube_summarizer")


class OpenRouterClient:
    """OpenRouter client with JSON output and model fallback."""

    def __init__(self) -> None:
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is missing."
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        self.models = get_models()
        self.max_retries = 2

    def summarize_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        """Generate a JSON response and parse it."""

        response = self._request(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        return self._parse_json(response)

    def _request(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Try configured models until valid JSON is returned."""

        last_error: Exception | None = None

        for model in self.models:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(
                        "Trying AI model: %s (attempt %s/%s)",
                        model,
                        attempt,
                        self.max_retries,
                    )

                    messages = []

                    if system_prompt:
                        messages.append(
                            {
                                "role": "system",
                                "content": system_prompt,
                            }
                        )

                    messages.append(
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    )

                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.2,
                        max_tokens=4000,
                        response_format={
                            "type": "json_object"
                        },
                        extra_body={
                            "reasoning": {
                                "exclude": True
                            }
                        },
                        timeout=60.0,
                    )

                    if not response.choices:
                        raise RuntimeError(
                            "No choices returned from AI."
                        )

                    content = response.choices[0].message.content

                    if not content or not content.strip():
                        raise RuntimeError(
                            "Empty AI response."
                        )

                    content = content.strip()

                    try:
                        parsed = self._parse_json(
                            content
                        )

                    except (ValueError, TypeError) as exc:
                        raise RuntimeError(
                            "AI returned invalid JSON."
                        ) from exc

                    logger.info(
                        "AI model succeeded: %s",
                        model,
                    )

                    return json.dumps(
                        parsed,
                        ensure_ascii=False,
                    )

                except Exception as exc:
                    last_error = exc

                    logger.warning(
                        "AI model failed: %s | %s",
                        model,
                        str(exc)[:500],
                    )

                    error_text = str(exc).lower()

                    retryable = (
                        "429" in error_text
                        or "timeout" in error_text
                        or "timed out" in error_text
                        or "rate limit" in error_text
                        or "temporarily unavailable"
                        in error_text
                        or "invalid json"
                        in error_text
                    )

                    if (
                        retryable
                        and attempt < self.max_retries
                    ):
                        delay = 2 ** (attempt - 1)

                        logger.info(
                            "Retrying AI request in %s seconds...",
                            delay,
                        )

                        time.sleep(delay)

                        continue

                    break

        raise RuntimeError(
            f"All AI models failed: {last_error}"
        )

    def _parse_json(
        self,
        text: str,
    ) -> dict:
        """Parse JSON from a model response."""

        if not text or not text.strip():
            raise ValueError(
                "Empty AI response."
            )

        text = text.strip()

        # Direct JSON
        try:
            result = json.loads(text)

        except json.JSONDecodeError:
            result = None

        else:
            if not isinstance(result, dict):
                raise TypeError(
                    "AI response must be a JSON object."
                )

            return result

        # Markdown JSON block
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        ).strip()

        try:
            result = json.loads(cleaned)

        except json.JSONDecodeError:
            result = None

        else:
            if not isinstance(result, dict):
                raise TypeError(
                    "AI response must be a JSON object."
                )

            return result

        # JSON object embedded inside additional text
        match = re.search(
            r"\{.*\}",
            cleaned,
            re.DOTALL,
        )

        if match:
            candidate = match.group().strip()

            try:
                result = json.loads(candidate)

            except json.JSONDecodeError:
                result = None

            else:
                if not isinstance(result, dict):
                    raise TypeError(
                        "AI response must be a JSON object."
                    )

                return result

        logger.error(
            "Invalid AI JSON response: %s",
            text[:2000],
        )

        raise ValueError(
            "AI response does not contain valid JSON."
        )

