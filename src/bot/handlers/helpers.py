import logging
from typing import Any

from telegram import Update, Message
from telegram.error import BadRequest, TimedOut, NetworkError

logger = logging.getLogger("youtube_summarizer")


async def safe_reply(update: Update, text: str, **kwargs: Any) -> Message:
    return await update.message.reply_text(text, **kwargs)


async def safe_delete(message: Message) -> None:
    try:
        await message.delete()
    except BadRequest as e:
        logger.warning(f"Failed to delete message {message.message_id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error deleting message {message.message_id}: {e}")


async def safe_edit(message: Message, text: str, **kwargs: Any) -> None:
    try:
        await message.edit_text(text, **kwargs)
    except BadRequest as e:
        if "Message is not modified" in str(e):
            pass
        else:
            logger.warning(f"Failed to edit message {message.message_id}: {e}")
    except (TimedOut, NetworkError) as e:
        logger.error(f"Network error editing message (VPN/Proxy issue?): {e}")
    except Exception as e:
        logger.error(f"Unexpected error editing message {message.message_id}: {e}")


async def send_long_message(update: Update, text: str) -> None:
    LIMIT = 4096
    if len(text) <= LIMIT:
        await update.message.reply_text(text)
        return

    start = 0
    while start < len(text):
        end = start + LIMIT
        await update.message.reply_text(text[start:end])
        start = end


class StatusMessage:
    def __init__(self, message: Message):
        self.message = message

    async def update(self, text: str, **kwargs: Any) -> None:
        try:
            await self.message.edit_text(text, **kwargs)
        except BadRequest as e:
            if "Message is not modified" not in str(e):
                logger.warning(f"Failed to update status message: {e}")
        except (TimedOut, NetworkError) as e:
            logger.error(f"Network error updating status (VPN/Proxy issue?): {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating status message: {e}")

    async def delete(self) -> None:
        await safe_delete(self.message)