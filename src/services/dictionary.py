import httpx
import logging

logger = logging.getLogger("youtube_summarizer")

FREE_DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"

async def get_definition(term: str) -> str:
    """
    Fetches the definition of a term from Free Dictionary API.
    Returns the term with its definition if found, otherwise just the term.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # حذف کاراکترهای اضافی از کلمه
            clean_term = term.strip().replace("-", " ")
            response = await client.get(f"{FREE_DICT_API}{clean_term}")
            
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and "meanings" in data[0]:
                    meanings = data[0]["meanings"]
                    if meanings and "definitions" in meanings[0]:
                        definition = meanings[0]["definitions"][0]["definition"]
                        # بازگرداندن کلمه به همراه معنی
                        return f"{term}:\n   ↳ {definition}"
            # اگر کلمه پیدا نشد یا خطا داد
            return term
            
    except Exception as e:
        logger.warning(f"Dictionary lookup failed for '{term}': {e}")
        return term


async def enrich_terms_with_definitions(terms: list) -> list:
    """
    Enrich a list of extracted terms with their definitions.
    """
    if not terms:
        return []
    
    enriched = []
    for term in terms:
        enriched_term = await get_definition(term)
        enriched.append(enriched_term)
        
    return enriched