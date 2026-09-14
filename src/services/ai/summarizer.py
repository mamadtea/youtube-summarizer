
import logging
from typing import Any

from src.services.ai.map_reduce import MapReduceSummarizer

logger = logging.getLogger("youtube_summarizer")


class SummarizerService:
    def __init__(self) -> None:
        self.engine = MapReduceSummarizer()

    def summarize(
        self,
        transcript: str,
        language: str = "Persian",
        summary_type: str = "complete",
        context_hint: str = "a YouTube video transcript",
    ) -> dict[str, Any]:
        logger.info(
            "Starting summarization | language=%s | type=%s",
            language,
            summary_type,
        )

        result = self.engine.summarize(
            transcript=transcript,
            language=language,
            summary_type=summary_type,
            context_hint=context_hint,
        )

        logger.info(
            "Summarization completed successfully"
        )

        return result

