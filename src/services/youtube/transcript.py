from youtube_transcript_api import YouTubeTranscriptApi



class TranscriptService:
    """
    Service responsible for getting YouTube transcripts.

    Priority:
    1. Persian transcript
    2. English transcript
    3. Any available transcript
    """



    def __init__(self):

        self.api = YouTubeTranscriptApi()



    def get(
        self,
        video_id: str
    ) -> str:
        """
        Get transcript text from YouTube.

        Args:
            video_id:
                YouTube video id

        Returns:
            Full transcript text
        """



        try:

            transcript = self.api.fetch(
                video_id,
                languages=[
                    "fa",
                    "en"
                ]
            )


            return self._convert(
                transcript
            )



        except Exception:


            return self._fallback(
                video_id
            )





    def _fallback(
        self,
        video_id: str
    ) -> str:
        """
        Use any available transcript.
        """



        transcripts = (
            self.api.list(
                video_id
            )
        )



        for transcript in transcripts:


            result = transcript.fetch()


            return self._convert(
                result
            )



        raise Exception(
            "No transcript available for this video"
        )







    def _convert(
        self,
        transcript
    ) -> str:
        """
        Convert transcript objects
        into plain text.
        """



        texts = []


        for item in transcript:

            texts.append(
                item.text
            )



        return "\n".join(
            texts
        )