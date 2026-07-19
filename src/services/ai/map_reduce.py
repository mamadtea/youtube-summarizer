import json
import logging

from src.services.ai.chunker import TranscriptChunker
from src.services.ai.openrouter_client import OpenRouterClient
from src.services.ai.parser import SummaryParser

logger = logging.getLogger("youtube_summarizer")


class MapReduceSummarizer:
    def __init__(self):
        self.chunker = TranscriptChunker()
        self.client = OpenRouterClient()
        self.parser = SummaryParser()

    def _get_style_instruction(self, summary_type: str) -> str:
        """Returns specific prompt instructions based on the summary type."""
        if summary_type == "brief":
            return """
STYLE: BRIEF (کوتاه)
- Write a very concise and to-the-point summary (1-2 short paragraphs).
- Only list the 2 or 3 MOST CRITICAL key points.
- Keep the terms and conclusion very brief.
"""
        elif summary_type == "educational":
            return """
STYLE: EDUCATIONAL (آموزشی)
- Structure the summary like a tutorial or a lesson.
- Explain concepts simply, as if teaching a beginner.
- In "terms", include technical words and briefly explain them (e.g., "API: A way for software to communicate").
- In "conclusion", summarize what the user should have learned (Learning Outcomes).
"""
        else:  # complete (default)
            return """
STYLE: COMPLETE (کامل)
- Write a comprehensive, detailed, and thorough summary covering all aspects of the video.
- List ALL important key points (at least 5-7 points).
- Ensure no significant detail from the video is missed.
- Provide a deep and insightful final conclusion.
"""

    def summarize(
        self,
        transcript: str,
        language: str = "Persian",
        summary_type: str = "complete"
    ) -> dict:

        error_result = {
            "summary": "",
            "key_points": [],
            "terms": [],
            "conclusion": ""
        }

        chunks = self.chunker.split(transcript)
        if not chunks:
            error_result["summary"] = "❌ متنی برای خلاصه‌سازی یافت نشد (ویدیو زیرنویس ندارد)."
            return error_result

        style_instruction = self._get_style_instruction(summary_type)
        partial_summaries = []

        for index, chunk in enumerate(chunks):
            logger.info(f"Summarizing chunk {index + 1}/{len(chunks)}")
            
            try:
                summary = self.client.summarize_json(
                    system_prompt=f"""
You are a YouTube summarizer.
{style_instruction}
Extract info from the transcript section.
Return ONLY valid JSON with these exact keys:
"summary": "The summary of this section based on the style",
"key_points": ["list of key points"],
"terms": ["list of technical terms or jargon"]
Do NOT use "overview". Use "summary".
""",
                    user_prompt=f"""
Language: {language}

Transcript section:
{chunk}
"""
                )

                if summary and not summary.get("error"):
                    partial_summaries.append(summary)
                elif summary and summary.get("error"):
                    partial_summaries.append({"summary": summary.get("raw", "")})

            except Exception as e:
                error_msg = str(e)
                logger.exception(f"Chunk {index + 1} failed: {error_msg}")
                error_result["summary"] = f"❌ خطا در ارتباط با هوش مصنوعی:\n`{error_msg}`"
                return error_result

        if not partial_summaries:
            error_result["summary"] = "❌ هوش مصنوعی نتوانست هیچ بخشی را تحلیل کند."
            return error_result

        combined = "\n\n".join(
            [
                f"SECTION {i + 1}\n{json.dumps(item, ensure_ascii=False)}"
                for i, item in enumerate(partial_summaries)
            ]
        )

        try:
            final_result = self.client.summarize_json(
                system_prompt=f"""
You are an expert YouTube video summarizer.
{style_instruction}
Combine the sections into ONE final summary.
You MUST return a valid JSON object with EXACTLY these keys:
"summary", "key_points", "terms", "conclusion".
Do NOT leave the "summary" field empty.
Do NOT leave the "conclusion" field empty.
""",
                user_prompt=f"""
Language: {language}

Required JSON Format:
{{
"summary": "Write the main summary based on the requested style",
"key_points": ["List of the key points based on the requested style"],
"terms": ["List of terms based on the requested style"],
"conclusion": "Write the conclusion based on the requested style"
}}

Input summaries:
{combined}
"""
            )

            if not final_result or final_result.get("error"):
                raw_fallback = final_result.get("raw", "") if final_result else ""
                if raw_fallback:
                    error_result["summary"] = raw_fallback
                    return error_result
                    
                raise Exception("Reduce phase returned empty or error.")

            parsed = self.parser.parse(final_result)
            
            if not parsed or not parsed.get("summary"):
                raise Exception("Parser returned empty summary.")

            return {
                "summary": parsed.get("summary", ""),
                "key_points": parsed.get("key_points", []),
                "terms": parsed.get("terms", []),
                "conclusion": parsed.get("conclusion", "")
            }

        except Exception as e:
            error_msg = str(e)
            logger.exception(f"Reduce failed: {error_msg}")
            fallback_text = "\n\n".join([p.get("summary", "") for p in partial_summaries if p.get("summary")])
            if fallback_text:
                error_result["summary"] = fallback_text
            else:
                error_result["summary"] = f"❌ خطا در تولید خلاصه نهایی:\n`{error_msg}`"
            return error_result