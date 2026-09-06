import os
import logging
from typing import Optional
from yt_dlp import YoutubeDL

logger = logging.getLogger("youtube_summarizer")

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


class InstagramService:
    """
    Extracts caption and downloads audio from Instagram posts/reels.
    """

    def __init__(self):
        self.info_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
        }
        
        # تنظیمات برای دانلود فقط صدا (mp3)
        self.audio_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best',
            'outtmpl': f'{TEMP_DIR}/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64', # کیفیت پایین برای مصرف اینترنت و حجم کمتر به API
            }],
        }

    def get_info(self, url: str) -> Optional[dict]:
        """Extracts only metadata and caption."""
        try:
            with YoutubeDL(self.info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None

                caption = info.get("description", "")
                title = info.get("title", "Instagram Post")
                uploader = info.get("uploader", "Unknown")
                post_id = info.get("id", "unknown_id")

                return {
                    "id": post_id,
                    "title": title,
                    "channel": uploader,
                    "caption": caption if caption else ""
                }
        except Exception as e:
            logger.exception(f"Error extracting Instagram info: {e}")
            return None

    def download_audio(self, url: str, post_id: str) -> Optional[str]:
        """Downloads the audio of the reel and returns the file path."""
        try:
            # تنظیم نام فایل خروجی بر اساس آیدی پست
            self.audio_opts['outtmpl'] = f'{TEMP_DIR}/{post_id}.%(ext)s'
            
            with YoutubeDL(self.audio_opts) as ydl:
                ydl.download([url])
                
                # مسیر فایل mp3 که باید ساخته شده باشد
                audio_path = os.path.join(TEMP_DIR, f"{post_id}.mp3")
                if os.path.exists(audio_path):
                    return audio_path
                return None
                
        except Exception as e:
            logger.exception(f"Error downloading Instagram audio: {e}")
            return None


# Singleton
instagram_service = InstagramService()