import json
import logging
import re

from src.services.ai.schemas import SummarySchema

logger = logging.getLogger("youtube_summarizer")


class SummaryParser:
    def parse(self, data: any) -> dict:
        raw_text = ""
        dict_data = {}

        if isinstance(data, str):
            raw_text = data
        elif isinstance(data, dict):
            if "error" in data and "raw" in data:
                raw_text = data["raw"]
            else:
                dict_data = data
        
        if raw_text:
            try:
                clean_str = re.sub(r'^```(?:json)?\s*', '', raw_text.strip())
                clean_str = re.sub(r'\s*```$', '', clean_str.strip())
                dict_data = json.loads(clean_str)
            except json.JSONDecodeError:
                logger.warning("AI returned plain text instead of JSON. Using as summary.")
                return {
                    "summary": raw_text,
                    "key_points": [],
                    "terms": [],
                    "conclusion": ""
                }

        summary = (
            dict_data.get("summary") or 
            dict_data.get("overview") or 
            dict_data.get("text") or 
            dict_data.get("content") or 
            ""
        )
        
        key_points = (
            dict_data.get("key_points") or 
            dict_data.get("key points") or 
            dict_data.get("points") or 
            []
        )
        
        terms = (
            dict_data.get("terms") or 
            dict_data.get("important_terms") or 
            dict_data.get("jargon") or 
            dict_data.get("keywords") or 
            []
        )
        
        conclusion = (
            dict_data.get("conclusion") or 
            dict_data.get("final_takeaway") or 
            dict_data.get("takeaway") or 
            ""
        )

        if not summary and dict_data:
            longest_text = ""
            for value in dict_data.values():
                if isinstance(value, str) and len(value) > len(longest_text):
                    longest_text = value
            summary = longest_text

        if isinstance(key_points, str): 
            key_points: list[str] = [key_points]
        if isinstance(terms, str): 
            terms: list[str] = [terms]  

        try:
            result = SummarySchema(
                summary=summary,
                key_points=key_points,
                terms=terms,
                conclusion=conclusion
            ) 
            return result.model_dump()
            
        except Exception as e:
            logger.error(f"Final Schema validation error: {e}")
            return {
                "summary": summary,
                "key_points": key_points,
                "terms": terms,
                "conclusion": conclusion
            }