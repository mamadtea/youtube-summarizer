import time
import logging


logger = logging.getLogger(
    "youtube_summarizer"
)



class SummaryCache:
    """
    Cache system for generated summaries.

    Key structure:

    video_url + language + summary_type

    Example:

    youtube_url|Persian|detailed
    """



    def __init__(
        self,
        expire_seconds: int = 86400
    ):

        self.cache = {}

        self.expire_seconds = expire_seconds



    # =====================================
    # CREATE KEY
    # =====================================


    def _create_key(
        self,
        video_id: str,
        language: str,
        summary_type: str
    ):


        return (
            f"{video_id}"
            "|"
            f"{language}"
            "|"
            f"{summary_type}"
        )



    # =====================================
    # SET
    # =====================================


    def set(
        self,
        video_id: str,
        language: str,
        summary_type: str,
        value: dict
    ):

        """
        Save summary in cache.
        """


        key = self._create_key(

            video_id,

            language,

            summary_type

        )



        self.cache[key] = {

            "data": value,

            "created": time.time()

        }



        logger.info(

            f"Cache saved: {key}"

        )



    # =====================================
    # GET
    # =====================================


    def get(
        self,
        video_id: str,
        language: str,
        summary_type: str
    ):

        """
        Get cached summary.
        """


        key = self._create_key(

            video_id,

            language,

            summary_type

        )



        item = self.cache.get(
            key
        )



        if not item:

            return None




        # check expiration


        if (

            time.time()

            -

            item["created"]

            >

            self.expire_seconds

        ):


            self.delete(

                video_id,

                language,

                summary_type

            )


            return None




        logger.info(

            f"Cache hit: {key}"

        )



        return item["data"]



    # =====================================
    # DELETE
    # =====================================


    def delete(
        self,
        video_id: str,
        language: str,
        summary_type: str
    ):


        key = self._create_key(

            video_id,

            language,

            summary_type

        )


        if key in self.cache:


            del self.cache[key]


            logger.info(

                f"Cache deleted: {key}"

            )



    # =====================================
    # EXISTS
    # =====================================


    def exists(
        self,
        video_id: str,
        language: str,
        summary_type: str
    ) -> bool:


        return (

            self.get(

                video_id,

                language,

                summary_type

            )

            is not None

        )



    # =====================================
    # CLEAR
    # =====================================


    def clear(
        self
    ):


        self.cache.clear()


        logger.info(

            "Cache cleared"

        )



    # =====================================
    # SIZE
    # =====================================


    def size(
        self
    ):


        return len(
            self.cache
        )