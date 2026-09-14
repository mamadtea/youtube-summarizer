
import logging
from typing import Any

from telegram import Message
from telegram.error import BadRequest, NetworkError, TimedOut

logger = logging.getLogger("youtube_summarizer")


async def safe_edit(
    message: Message,
    text: str,
    **kwargs: Any,
) -> None:
    try:
        await message.edit_text(
            text,
            **kwargs,
        )

    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.warning(
                "Failed to edit message %s: %s",
                message.message_id,
                e,
            )

    except (TimedOut, NetworkError) as e:
        logger.error(
            "Network error editing message %s: %s",
            message.message_id,
            e,
        )


class StatusMessage:
    def __init__(self, message: Message):
        self.message = message

    async def update(
        self,
        text: str,
        **kwargs: Any,
    ) -> None:
        try:
            await self.message.edit_text(
                text,
                **kwargs,
            )

        except BadRequest as e:
            if "Message is not modified" not in str(e):
                logger.warning(
                    "Failed to update status message: %s",
                    e,
                )

        except (TimedOut, NetworkError) as e:
            logger.error(
                "Network error updating status message: %s",
                e,
            )

