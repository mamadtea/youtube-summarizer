class TranscriptChunker:
    """
    Splits long transcripts into smaller pieces.
    """

    def __init__(
        self,
        chunk_size=2500,
        overlap=200
    ):

        self.chunk_size = chunk_size
        self.overlap = overlap



    def split(
        self,
        text: str
    ) -> list:


        if not text:

            return []



        chunks = []

        start = 0

        text_length = len(text)



        while start < text_length:


            end = min(

                start + self.chunk_size,

                text_length

            )



            chunk = text[start:end]



            chunks.append(

                chunk

            )



            # رسیدن به آخر متن

            if end >= text_length:

                break



            start = end - self.overlap



        return chunks