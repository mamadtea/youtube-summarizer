from yt_dlp import YoutubeDL

from src.models.video import Video


class YouTubeInfoService:

    def get(self, url: str) -> Video:

        options = {
            "quiet": True,
            "skip_download": True,
        }

        with YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=False,
            )

        return Video(
            id=info["id"],
            url=url,
            title=info.get("title", ""),
            channel=info.get("channel", ""),
            duration=info.get("duration", 0),
            description=info.get("description", ""),
            thumbnail=info.get("thumbnail", ""),
        )