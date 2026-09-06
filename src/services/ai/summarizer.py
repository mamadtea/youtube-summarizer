import logging
from typing import Dict, Any
from src.services.ai.map_reduce import MapReduceSummarizer

logger = logging.getLogger("youtube_summarizer")


class SummarizerService:
    def __init__(self):
        self.engine = MapReduceSummarizer()

    def summarize(self, transcript: str, language: str = "Persian", summary_type: str = "complete", context_hint: str = "a YouTube video transcript") -> Dict[str, Any]:
        logger.info(f"Starting summarization | Lang: {language} | Type: {summary_type}")
        try:
            return self.engine.summarize(transcript=transcript, language=language, summary_type=summary_type, context_hint=context_hint)
        except Exception as e:
            logger.exception(f"Summarization failed: {e}")
            return {"summary": "خطایی در سیستم رخ داده است.", "key_points": [], "terms": [], "conclusion": ""}