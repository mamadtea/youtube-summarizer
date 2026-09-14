
import json
import logging

from src.services.ai.openrouter_client import OpenRouterClient
from src.services.ai.parser import SummaryParser

logger = logging.getLogger("youtube_summarizer")


class MapReduceSummarizer:
    def __init__(self) -> None:
        self.client = OpenRouterClient()
        self.parser = SummaryParser()

    def _get_style_instruction(
        self,
        summary_type: str,
    ) -> str:
        if summary_type == "brief":
            return (
                "STYLE: BRIEF. "
                "Write a short summary in 1-2 paragraphs. "
                "Provide only 3 critical key points. "
                "Keep terms and conclusion short."
            )

        if summary_type == "educational":
            return (
                "STYLE: EDUCATIONAL. "
                "Explain the important concepts clearly for beginners. "
                "Use simple language. "
                "In 'terms', include important technical terms. "
                "In 'conclusion', explain what the user should learn."
            )

        return (
            "STYLE: COMPLETE. "
            "Write a detailed but concise summary. "
            "Include the most important information. "
            "Avoid unnecessary repetition."
        )

    def _split_transcript(
        self,
        transcript: str,
    ) -> list[str]:
        """
        Split transcript into manageable sections.

        The current implementation processes the transcript
        as one section. A dedicated chunker can be introduced
        later without changing the public summarize() API.
        """

        text = transcript.strip()

        if not text:
            return []

        return [text]

    def _normalize_partial_summary(
        self,
        result: dict,
    ) -> dict:
        """Normalize a partial AI response."""

        summary = result.get(
            "summary",
            "",
        )

        key_points = result.get(
            "key_points",
            [],
        )

        terms = result.get(
            "terms",
            [],
        )

        conclusion = result.get(
            "conclusion",
            "",
        )

        if not isinstance(summary, str):
            summary = str(summary)

        if not isinstance(key_points, list):
            key_points = []

        if not isinstance(terms, list):
            terms = []

        if not isinstance(conclusion, str):
            conclusion = str(conclusion)

        if not summary.strip():
            raise ValueError(
                "AI partial summary is empty."
            )

        return {
            "summary": summary.strip(),
            "key_points": key_points,
            "terms": terms,
            "conclusion": conclusion.strip(),
        }

    def summarize(
        self,
        transcript: str,
        language: str = "Persian",
        summary_type: str = "complete",
        context_hint: str = "a YouTube video transcript",
    ) -> dict:
        if not transcript or not transcript.strip():
            raise ValueError(
                "Transcript is empty."
            )

        style_instruction = self._get_style_instruction(
            summary_type
        )

        chunks = self._split_transcript(
            transcript
        )

        if not chunks:
            raise ValueError(
                "No transcript chunks were created."
            )

        partial_summaries: list[dict] = []

        # Map phase
        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            logger.info(
                "Processing transcript chunk %s/%s",
                index,
                len(chunks),
            )

            partial_result = self.client.summarize_json(
                system_prompt=(
                    "You are a content summarizer. "
                    f"You are reading {context_hint}. "
                    f"{style_instruction} "
                    "Return ONLY valid JSON. "
                    "Do not use Markdown. "
                    "Do not use ```json or ``` fences. "
                    "The JSON object must contain exactly these fields: "
                    "'summary', 'key_points', 'terms', 'conclusion'. "
                    "Keep the response concise enough to fit the output limit."
                ),
                user_prompt=(
                    f"Language: {language}\n\n"
                    "Summarize the following section:\n\n"
                    f"{chunk}"
                ),
            )

            if not isinstance(partial_result, dict):
                raise TypeError(
                    "AI partial response must be a JSON object."
                )

            normalized = self._normalize_partial_summary(
                partial_result
            )

            partial_summaries.append(
                normalized
            )

        if not partial_summaries:
            raise RuntimeError(
                "No partial summaries were generated."
            )

        # Reduce phase
        sections = []

        for index, item in enumerate(
            partial_summaries,
            start=1,
        ):
            sections.append(
                
                    f"SECTION {index}\n"
                    f"Summary: {item['summary']}\n"
                    f"Key points: "
                    f"{json.dumps(item['key_points'], ensure_ascii=False)}\n"
                    f"Terms: "
                    f"{json.dumps(item['terms'], ensure_ascii=False)}\n"
                    f"Conclusion: {item['conclusion']}"
                
            )

        combined = "\n\n".join(
            sections
        )

        logger.info(
            "Starting reduce phase with %s sections",
            len(partial_summaries),
        )

        final_result = self.client.summarize_json(
            system_prompt=(
                "You are an expert summarizer. "
                f"You are summarizing {context_hint}. "
                f"{style_instruction} "
                "Combine the provided sections into one final answer. "
                "Remove duplicated information. "
                "Keep only the most important points. "
                "Do not invent information. "
                "Return ONLY valid JSON. "
                "Do not use Markdown. "
                "Do not use ```json or ``` fences. "
                "The JSON object must contain exactly these fields: "
                "'summary', 'key_points', 'terms', 'conclusion'. "
                "Keep the output concise so the JSON is always complete."
            ),
            user_prompt=(
                f"Language: {language}\n\n"
                "Combine these section summaries:\n\n"
                f"{combined}"
            ),
        )

        if not isinstance(final_result, dict):
            raise TypeError(
                "Final AI response must be a JSON object."
            )

        parsed = self.parser.parse(
            final_result
        )

        if not parsed:
            raise ValueError(
                "Summary parser returned an empty result."
            )

        summary_text = parsed.get(
            "summary",
            "",
        )

        if not isinstance(summary_text, str):
            summary_text = str(summary_text)

        if not summary_text.strip():
            raise ValueError(
                "Final summary is empty."
            )

        key_points = parsed.get(
            "key_points",
            [],
        )

        terms = parsed.get(
            "terms",
            [],
        )

        conclusion = parsed.get(
            "conclusion",
            "",
        )

        if not isinstance(key_points, list):
            key_points = []

        if not isinstance(terms, list):
            terms = []

        if not isinstance(conclusion, str):
            conclusion = str(conclusion)

        logger.info(
            "Map-reduce summarization completed successfully"
        )

        return {
            "summary": summary_text.strip(),
            "key_points": key_points,
            "terms": terms,
            "conclusion": conclusion.strip(),
        }

