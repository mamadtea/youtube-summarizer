from src.models.video import Video

from src.services.youtube.info import YouTubeInfoService
from src.services.youtube.transcript import TranscriptService



class YouTubeService:
    """
    Complete YouTube processing pipeline.

    Flow:

    YouTube URL
        ↓
    Video Information
        ↓
    Transcript
        ↓
    Complete Video Object
    """


    def __init__(self):

        self.info_service = YouTubeInfoService()

        self.transcript_service = TranscriptService()



    def process(
        self,
        url: str
    ) -> Video:
        """
        Process YouTube URL.

        Returns:
            Video object with:
            - title
            - url
            - duration
            - transcript
        """


        video = self.info_service.get(
            url
        )


        video.transcript = (
            self.transcript_service.get(
                video.id
            )
        )


        return video