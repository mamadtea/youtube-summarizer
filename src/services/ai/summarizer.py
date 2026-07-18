from src.services.ai.map_reduce import MapReduceSummarizer



class SummarizerService:
    """
    Main AI summarization service.
    """


    def __init__(self):

        self.engine = MapReduceSummarizer()



    def summarize(
        self,
        transcript: str,
        language: str = "Persian",
        summary_type: str = "detailed"
    ) -> dict:


        return self.engine.summarize(

            transcript=transcript,

            language=language,

            summary_type=summary_type
        )