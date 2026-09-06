import httpx
import logging
import os

logger = logging.getLogger("youtube_summarizer")
SUPRSONIC_STT_URL = "https://api.suprsonic.ai/v1/stt" 


async def transcribe_audio(audio_path: str, language: str = "fa") -> str:
    from src.config.settings import SUPRSONIC_API_KEY

    if not SUPRSONIC_API_KEY or SUPRSONIC_API_KEY == "YOUR_SUPRSONIC_API_KEY":
        logger.warning("Suprsonic API Key is not set. Skipping STT.")
        return ""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(audio_path, "rb") as audio_file:
                files = {"file": (os.path.basename(audio_path), audio_file, "audio/mpeg")}
                headers = {"Authorization": f"Bearer {SUPRSONIC_API_KEY}"}
                data = {"language": language} 
                
                response = await client.post(SUPRSONIC_STT_URL, headers=headers, files=files, data=data)
                response.raise_for_status()
                
                result = response.json()
                if isinstance(result, dict):
                    return result.get("text", result.get("transcript", ""))
                elif isinstance(result, list) and len(result) > 0:
                    return result[0].get("text", "")
                return ""
    except Exception as e:
        logger.error(f"Suprsonic STT failed: {e}")
        return ""