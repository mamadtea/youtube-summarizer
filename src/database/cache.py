import time
import logging


logger = logging.getLogger(
    "youtube_summarizer"
)


class SummaryCache:
    """
    Simple in-memory cache for video summaries.
    """


    def __init__(
        self,
        expire_seconds: int = 3600
    ):

        self.cache = {}

        self.expire_seconds = expire_seconds



    # ==================================
    # SET CACHE
    # ==================================

    def set(
        self,
        key: str,
        value: dict
    ):

        """
        Store summary result.
        """

        self.cache[key] = {

            "data": value,

            "time": time.time()

        }


        logger.info(

            f"Cache saved: {key}"

        )




    # ==================================
    # GET CACHE
    # ==================================

    def get(
        self,
        key: str
    ):

        """
        Get cached summary.
        """


        item = self.cache.get(
            key
        )


        if not item:

            return None



        # check expiration

        if (
            time.time()
            -
            item["time"]
            >
            self.expire_seconds
        ):


            self.delete(
                key
            )


            return None




        logger.info(

            f"Cache hit: {key}"

        )


        return item["data"]





    # ==================================
    # DELETE CACHE
    # ==================================

    def delete(
        self,
        key: str
    ):


        if key in self.cache:


            del self.cache[key]


            logger.info(

                f"Cache deleted: {key}"

            )





    # ==================================
    # CLEAR ALL
    # ==================================

    def clear(
        self
    ):

        """
        Clear cache.
        """


        self.cache.clear()


        logger.info(

            "Cache cleared"

        )





    # ==================================
    # EXISTS
    # ==================================

    def exists(
        self,
        key: str
    ) -> bool:


        return self.get(key) is not None
    # =====================================
# Singleton
# =====================================

_cache = SummaryCache()


def set(
    key: str,
    value: dict
):
    _cache.set(
        key,
        value
    )


def get(
    key: str
):
    return _cache.get(
        key
    )


def delete(
    key: str
):
    _cache.delete(
        key
    )


def clear():
    _cache.clear()


def exists(
    key: str
):
    return _cache.exists(
        key
    )