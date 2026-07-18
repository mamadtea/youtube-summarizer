import logging
import os



def setup_logger():


    log_level = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )


    logging.basicConfig(

        level=getattr(
            logging,
            log_level
        ),

        format=
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",

        handlers=[

            logging.FileHandler(
                "bot.log",
                encoding="utf-8"
            ),

            logging.StreamHandler()

        ]

    )


    return logging.getLogger(
        "youtube_summarizer"
    )