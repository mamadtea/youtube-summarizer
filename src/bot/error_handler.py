import logging

from telegram import Update
from telegram.ext import ContextTypes



logger = logging.getLogger(
    "youtube_summarizer"
)





async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):


    error = context.error



    logger.exception(
        "Telegram error occurred",
        exc_info=error
    )



    if isinstance(
        update,
        Update
    ):


        if update.message:


            await update.message.reply_text(
                """
⚠️ یک خطای غیرمنتظره رخ داد.

لطفاً چند لحظه بعد دوباره تلاش کنید.
"""
            )