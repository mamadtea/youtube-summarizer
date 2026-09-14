
import json
import logging
import re
from typing import Any

from src.services.ai.schemas import SummarySchema

logger = logging.getLogger("youtube_summarizer")


class SummaryParser:
    """Normalize and validate AI summary responses."""

    def parse(self, data: Any) -> dict:
        raw_text = ""
        dict_data: dict = {}

        if isinstance(data, str):
            raw_text = data

        elif isinstance(data, dict):
            if "error" in data and "raw" in data:
                raw_text = str(data["raw"])
            else:
                dict_data = data

        if raw_text:
            dict_data = self._parse_raw_json(raw_text)

            if not dict_data:
                return {
                    "summary": raw_text,
                    "key_points": [],
                    "terms": [],
                    "conclusion": "",
                }

        summary = (
            dict_data.get("summary")
            or dict_data.get("overview")
            or dict_data.get("text")
            or dict_data.get("content")
            or ""
        )

        key_points = (
            dict_data.get("key_points")
            or dict_data.get("key points")
            or dict_data.get("points")
            or []
        )

        terms = (
            dict_data.get("terms")
            or dict_data.get("important_terms")
            or dict_data.get("jargon")
            or dict_data.get("keywords")
            or []
        )

        conclusion = (
            dict_data.get("conclusion")
            or dict_data.get("final_takeaway")
            or dict_data.get("takeaway")
            or ""
        )

        if not summary and dict_data:
            summary = max(
                (
                    value
                    for value in dict_data.values()
                    if isinstance(value, str)
                ),
                key=len,
                default="",
            )

        key_points = self._normalize_string_list(
            key_points,
            "key_points",
        )

        terms = self._normalize_terms(
            terms
        )

        if not isinstance(conclusion, str):
            conclusion = str(conclusion)

        try:
            result = SummarySchema(
                summary=str(summary),
                key_points=key_points,
                terms=terms,
                conclusion=conclusion,
            )

            return result.model_dump(
                exclude_none=True
            )

        except Exception as exc:
            logger.error(
                "Schema validation error: %s",
                exc,
            )

            raise ValueError(
                "AI response failed schema validation."
            ) from exc

    def _parse_raw_json(
        self,
        raw_text: str,
    ) -> dict:
        """Parse JSON from raw AI text."""

        clean_str = re.sub(
            r"^```(?:json)?\s*",
            "",
            raw_text.strip(),
            flags=re.IGNORECASE,
        )

        clean_str = re.sub(
            r"\s*```$",
            "",
            clean_str.strip(),
        )

        try:
            result = json.loads(clean_str)

        except json.JSONDecodeError:
            match = re.search(
                r"\{.*\}",
                clean_str,
                re.DOTALL,
            )

            if not match:
                logger.warning(
                    "Could not parse AI response as JSON."
                )

                return {}

            try:
                result = json.loads(
                    match.group()
                )

            except json.JSONDecodeError:
                logger.warning(
                    "AI response contains invalid JSON."
                )

                return {}

        if not isinstance(result, dict):
            logger.warning(
                "AI JSON response is not an object."
            )

            return {}

        return result

    def _normalize_string_list(
        self,
        values: Any,
        field_name: str,
    ) -> list[str]:
        """Normalize a value into a list of strings."""

        if values is None:
            return []

        if isinstance(values, str):
            return [values]

        if not isinstance(values, list):
            logger.warning(
                "Invalid %s format. Expected a list.",
                field_name,
            )

            return []

        normalized: list[str] = []

        for item in values:
            if isinstance(item, str):
                value = item.strip()

                if value:
                    normalized.append(value)

            elif isinstance(item, dict):
                value = (
                    item.get("text")
                    or item.get("value")
                    or item.get("name")
                    or item.get("title")
                )

                if isinstance(value, str) and value.strip():
                    normalized.append(
                        value.strip()
                    )

        return normalized

    def _normalize_terms(
        self,
        values: Any,
    ) -> list[str]:
        """Normalize terms from strings or term objects."""

        if values is None:
            return []

        if isinstance(values, str):
            return [values.strip()]

        if not isinstance(values, list):
            logger.warning(
                "Invalid terms format. Expected a list."
            )

            return []

        normalized: list[str] = []

        for item in values:
            if isinstance(item, str):
                term = item.strip()

                if term:
                    normalized.append(term)

                continue

            if isinstance(item, dict):
                term = (
                    item.get("term")
                    or item.get("name")
                    or item.get("word")
                    or item.get("text")
                )

                if isinstance(term, str):
                    term = term.strip()

                    if term:
                        normalized.append(term)

        return normalized

