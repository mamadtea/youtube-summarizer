import logging
from typing import Any

from telegram import Message
from telegram.error import BadRequest, TimedOut, NetworkError

logger = logging.getLogger("youtube_summarizer")


async def safe_edit(message: Message, text: str, **kwargs: Any) -> None:
    try:
        await message.edit_text(text, **kwargs)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.warning(f"Failed to edit message {message.message_id}: {e}")
    except (TimedOut, NetworkError) as e:
        logger.error(f"Network error editing message (VPN/Proxy issue?): {e}")
    except Exception as e:
        logger.error(f"Unexpected error editing message {message.message_id}: {e}")


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
            logger.error(f"Network error updating status: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating status message: {e}")