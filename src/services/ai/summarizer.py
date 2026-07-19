import logging
from typing import Dict, Any

from src.services.ai.map_reduce import MapReduceSummarizer

logger = logging.getLogger("youtube_summarizer")


class SummarizerService:
    def __init__(self):
        self.engine = MapReduceSummarizer()

    def summarize(
        self,
        transcript: str,
        language: str = "Persian",
        summary_type: str = "detailed"
    ) -> Dict[str, Any]:
        logger.info(f"Starting summarization | Language: {language} | Type: {summary_type}")
        
        try:
            result = self.engine.summarize(
                transcript=transcript,
                language=language,
                summary_type=summary_type
            )
            logger.info("Summarization engine finished successfully.")
            return result
        except Exception as e:
            logger.exception(f"Summarization failed in engine: {e}")
            return {
                "summary": "خطایی در سیستم خلاصه‌سازی رخ داده است.",
                "key_points": [],
                "terms": [],
                "conclusion": ""
            }