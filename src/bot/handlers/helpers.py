from telegram import Update
from telegram import Message
from telegram.constants import ParseMode

from telegram.error import BadRequest


# =====================================================
# SAFE REPLY
# =====================================================

async def safe_reply(
    update: Update,
    text: str,
    **kwargs
):

    return await update.message.reply_text(
        text,
        **kwargs
    )


# =====================================================
# SAFE DELETE
# =====================================================

async def safe_delete(
    message: Message
):

    try:

        await message.delete()

    except Exception:

        pass


# =====================================================
# SAFE EDIT
# =====================================================

async def safe_edit(
    message: Message,
    text: str,
    **kwargs
):

    try:

        await message.edit_text(
            text,
            **kwargs
        )

    except BadRequest:

        pass

    except Exception:

        pass


# =====================================================
# LONG MESSAGE
# =====================================================

async def send_long_message(
    update: Update,
    text: str
):

    LIMIT = 4096

    if len(text) <= LIMIT:

        await update.message.reply_text(
            text
        )

        return

    start = 0

    while start < len(text):

        end = start + LIMIT

        await update.message.reply_text(
            text[start:end]
        )

        start = end


# =====================================================
# STATUS MESSAGE
# =====================================================

class StatusMessage:

    def __init__(self, message: Message):

        self.message = message


    async def update(
        self,
        text: str
    ):

        try:

            await self.message.edit_text(
                text
            )

        except Exception:

            pass


    async def delete(self):

        try:

            await self.message.delete()

        except Exception:

            pass