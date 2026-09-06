import httpx
import logging

logger = logging.getLogger("youtube_summarizer")
FREE_DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"


async def get_definition(term: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            clean_term = term.strip().replace("-", " ")
            response = await client.get(f"{FREE_DICT_API}{clean_term}")
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and "meanings" in data[0]:
                    meanings = data[0]["meanings"]
                    if meanings and "definitions" in meanings[0]:
                        definition = meanings[0]["definitions"][0]["definition"]
                        return f"{term}:\n   ↳ {definition}"
            return term
    except Exception as e:
        logger.warning(f"Dictionary lookup failed for '{term}': {e}")
        return term


async def enrich_terms_with_definitions(terms: list) -> list:
    if not terms:
        return []
    return [await get_definition(term) for term in terms]