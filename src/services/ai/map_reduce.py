import json
import logging

from src.services.ai.openrouter_client import OpenRouterClient
from src.services.ai.parser import SummaryParser

logger = logging.getLogger("youtube_summarizer")


class MapReduceSummarizer:
    def __init__(self):
        self.client = OpenRouterClient()
        self.parser = SummaryParser()

    def _get_style_instruction(self, summary_type: str) -> str:
        if summary_type == "brief":
            return "STYLE: BRIEF - Write 1-2 short paragraphs. Only 2-3 CRITICAL key points. Keep terms and conclusion very brief."
        elif summary_type == "educational":
            return 'STYLE: EDUCATIONAL - Structure like a lesson. Explain concepts for beginners. In "terms", include technical words and explain them. In "conclusion", summarize what the user should have learned.'
        return "STYLE: COMPLETE - Comprehensive, detailed, thorough summary. List ALL important key points. Provide deep final conclusion."

    def summarize(
        self,
        transcript: str,
        language: str = "Persian",
        summary_type: str = "complete",
        context_hint: str = "a YouTube video transcript"
    ) -> dict:

        error_result = {"summary": "", "key_points": [], "terms": [], "conclusion": ""}

        chunks = self.chunker.split(transcript) if hasattr(self, 'chunker') else [transcript]
        if not chunks:
            error_result["summary"] = "❌ متنی برای خلاصه‌سازی یافت نشد."
            return error_result

        style_instruction = self._get_style_instruction(summary_type)
        partial_summaries = []

        for index, chunk in enumerate(chunks):
            try:
                summary = self.client.summarize_json(
                    system_prompt=f"You are a content summarizer. You are reading {context_hint}. {style_instruction} Return ONLY valid JSON with: 'summary', 'key_points', 'terms', 'conclusion'",
                    user_prompt=f"Language: {language}\n\nText section:\n{chunk}"
                )
                if summary and not summary.get("error"):
                    partial_summaries.append(summary)
                elif summary and summary.get("error"):
                    partial_summaries.append({"summary": summary.get("raw", "")})
            except Exception as e:
                error_result["summary"] = f"❌ خطا در هوش مصنوعی:\n`{str(e)}`"
                return error_result

        if not partial_summaries:
            error_result["summary"] = "❌ تحلیل انجام نشد."
            return error_result

        combined = "\n\n".join([f"SECTION {i + 1}\n{json.dumps(item, ensure_ascii=False)}" for i, item in enumerate(partial_summaries)])

        try:
            final_result = self.client.summarize_json(
                system_prompt=f"You are an expert summarizer. You are summarizing {context_hint}. {style_instruction} Combine sections. Return ONLY valid JSON with: 'summary', 'key_points', 'terms', 'conclusion'",
                user_prompt=f"Language: {language}\n\nInput summaries:\n{combined}"
            )

            if not final_result or final_result.get("error"):
                if final_result and final_result.get("raw"):
                    error_result["summary"] = final_result["raw"]
                    return error_result
                raise Exception("Reduce phase empty")

            parsed = self.parser.parse(final_result)
            if not parsed or not parsed.get("summary"):
                raise Exception("Parser empty")

            return {"summary": parsed.get("summary", ""), "key_points": parsed.get("key_points", []), "terms": parsed.get("terms", []), "conclusion": parsed.get("conclusion", "")}
        except Exception as e:
            fallback_text = "\n\n".join([p.get("summary", "") for p in partial_summaries if p.get("summary")])
            error_result["summary"] = fallback_text if fallback_text else f"❌ خطا:\n`{str(e)}`"
            return error_result