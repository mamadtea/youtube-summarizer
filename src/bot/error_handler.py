import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError

logger = logging.getLogger("youtube_summarizer")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    error = context.error

    user_info = "Unknown user"
    if isinstance(update, Update) and update.effective_user:
        user_info = f"User {update.effective_user.id} ({update.effective_user.first_name})"
    
    logger.error(f"Exception while handling an update for {user_info}:", exc_info=error)

    if isinstance(error, TimedOut) or isinstance(error, NetworkError):
        text = "⏳ خطای ارتباط با سرورهای تلگرام. لطفاً دوباره تلاش کنید."
    elif isinstance(error, sqlite3.OperationalError):
        text = "🗄️ خطای موقت در پایگاه داده. لطفاً دوباره تلاش کنید."
    else:
        text = "⚠️ یک خطای غیرمنتظره رخ داد.\nلطفاً چند لحظه بعد دوباره تلاش کنید."

    if isinstance(update, Update):
        try:
            if update.callback_query:
                await update.callback_query.answer(text, show_alert=True)
            elif update.effective_message:
                await update.effective_message.reply_text(text)
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")