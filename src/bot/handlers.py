# ==========================================================
# YouTube Summarizer Bot
# handlers.py
# Professional Version
# ==========================================================


import logging
import asyncio


from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


from telegram.ext import (
    ContextTypes,
)


# ==========================================================
# PROJECT IMPORTS
# ==========================================================


from src.services.youtube.service import YouTubeService

from src.services.ai.summarizer import SummarizerService

from src.services.cache import SummaryCache

from src.database import history

from src.database import users


from src.bot.keyboards import (
    language_keyboard,
    summary_type_keyboard,
    settings_keyboard,
)


from src.utils.validators import (
    is_youtube_url,
)


# ==========================================================
# LOGGER
# ==========================================================


logger = logging.getLogger(
    "youtube_summarizer"
)



# ==========================================================
# SERVICES
# ==========================================================


youtube_service = YouTubeService()

summarizer_service = SummarizerService()

cache = SummaryCache()



# ==========================================================
# CONSTANTS
# ==========================================================


MAX_TELEGRAM_LENGTH = 4000



# ==========================================================
# DEFAULT USER MENU
# ==========================================================


def main_menu():

    keyboard = [

        [
            KeyboardButton(
                "⚙️ تنظیمات"
            ),

            KeyboardButton(
                "📚 تاریخچه"
            )
        ],


        [
            KeyboardButton(
                "👤 پروفایل"
            ),

            KeyboardButton(
                "❓ راهنما"
            )
        ]

    ]


    return ReplyKeyboardMarkup(

        keyboard,

        resize_keyboard=True

    )



# ==========================================================
# SAFE FUNCTIONS
# ==========================================================


async def safe_reply(
    update: Update,
    text: str,
    **kwargs
):

    try:

        if update.message:

            return await update.message.reply_text(
                text,
                **kwargs
            )


    except Exception as e:

        logger.error(
            f"Reply error: {e}"
        )



async def safe_edit(
    message,
    text,
    **kwargs
):

    try:

        return await message.edit_text(
            text,
            **kwargs
        )


    except Exception as e:

        logger.warning(
            f"Edit error: {e}"
        )



async def delete_message_safe(
    message
):

    try:

        await message.delete()


    except Exception:

        pass



# ==========================================================
# SEND LONG MESSAGE
# ==========================================================


async def send_long_message(
    update: Update,
    text: str
):


    if not text:

        return



    parts = [

        text[i:i + MAX_TELEGRAM_LENGTH]

        for i in range(
            0,
            len(text),
            MAX_TELEGRAM_LENGTH
        )

    ]



    for part in parts:


        await safe_reply(

            update,

            part

        )


        await asyncio.sleep(
            0.3
        )



# ==========================================================
# START COMMAND
# ==========================================================


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    user_id = update.effective_user.id



    users.create_if_not_exists(

        user_id

    )



    text = """

👋 سلام!

🤖 من ربات خلاصه‌ساز هوشمند یوتیوب هستم.


قابلیت‌ها:

🎬 خلاصه ویدیوهای یوتیوب

🧠 تحلیل محتوای آموزشی

📚 ذخیره تاریخچه

🌍 پشتیبانی چند زبان


لینک ویدیوی یوتیوب را ارسال کنید.


"""


    await safe_reply(

        update,

        text,

        reply_markup=main_menu()

    )


    logger.info(

        f"User started bot: {user_id}"

    )
    # ==========================================================
# HELP COMMAND
# ==========================================================


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    text = """

❓ راهنمای ربات


🎬 ارسال لینک یوتیوب:

فقط لینک ویدیو را ارسال کنید.


دستورات:

/start
شروع ربات


/settings
تنظیمات


/history
تاریخچه خلاصه‌ها


/me
پروفایل کاربر


/help
نمایش راهنما



"""


    await safe_reply(

        update,

        text,

        reply_markup=main_menu()

    )



# ==========================================================
# SETTINGS COMMAND
# ==========================================================


async def settings_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    await safe_reply(

        update,

        "⚙️ تنظیمات ربات:",

        reply_markup=settings_keyboard()

    )



# ==========================================================
# HISTORY COMMAND
# ==========================================================


async def history_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    user_id = update.effective_user.id



    try:

        items = history.get_history(

            user_id

        )



        if not items:


            await safe_reply(

                update,

                "📭 هنوز خلاصه‌ای ذخیره نشده است."

            )


            return



        text = "📚 تاریخچه خلاصه‌ها\n\n"



        for i, item in enumerate(

            items,

            start=1

        ):


            try:

                title = item["title"]

                created = item["created"]


            except:


                title = item[0]

                created = item[-1]



            text += (

                f"{i}️⃣ {title}\n"

                f"🕒 {created}\n\n"

            )



        await send_long_message(

            update,

            text

        )


    except Exception as e:


        logger.error(

            f"History error: {e}"

        )


        await safe_reply(

            update,

            "❌ دریافت تاریخچه ناموفق بود."

        )



# ==========================================================
# PROFILE COMMAND
# ==========================================================


async def me_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    user_id = update.effective_user.id



    try:


        user = users.get_user(

            user_id

        )


        if not user:

            user = {}



        text = f"""

👤 پروفایل


🆔 ID:

{user_id}


🌍 زبان:

{user.get("language","Persian")}


📝 نوع خلاصه:

{user.get("summary_type","detailed")}


📊 تعداد درخواست:

{user.get("requests",0)}


"""


        await safe_reply(

            update,

            text

        )


    except Exception as e:


        logger.error(

            f"Profile error: {e}"

        )



        await safe_reply(

            update,

            "❌ خطا در دریافت پروفایل."

        )



# ==========================================================
# CALLBACK HANDLERS
# ==========================================================



async def language_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    query = update.callback_query


    await query.answer()



    user_id = query.from_user.id



    language = query.data.split(":")[1]



    users.update(

        user_id,

        language=language

    )



    await query.edit_message_text(

        f"✅ زبان روی {language} تنظیم شد."

    )



# ==========================================================
# SUMMARY TYPE CALLBACK
# ==========================================================



async def summary_type_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    query = update.callback_query


    await query.answer()



    user_id = query.from_user.id



    summary_type = query.data.split(":")[1]



    users.update(

        user_id,

        summary_type=summary_type

    )



    await query.edit_message_text(

        "✅ نوع خلاصه تغییر کرد."

    )



# ==========================================================
# SETTINGS CALLBACK
# ==========================================================


async def settings_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    logger.info(

        "settings callback called"

    )


    query = update.callback_query


    await query.answer()



    action = query.data.split(":")[1]



    user_id = query.from_user.id



    if action == "language":


        await query.edit_message_text(

            "🌍 انتخاب زبان:",

            reply_markup=language_keyboard()

        )


        return



    if action == "summary":


        await query.edit_message_text(

            "📝 انتخاب نوع خلاصه:",

            reply_markup=summary_type_keyboard()

        )


        return



    if action == "profile":


        await query.edit_message_text(

            "برای مشاهده پروفایل از دستور /me استفاده کنید."

        )


        return



    if action == "history":


        items = history.get_history(

            user_id

        )



        if not items:


            await query.edit_message_text(

                "📭 تاریخچه خالی است."

            )


            return



        text = "📚 تاریخچه:\n\n"



        for index, item in enumerate(

            items,

            1

        ):


            text += (

                f"{index}. {item[0]}\n"

            )



        await query.edit_message_text(

            text[:4000]

        )


        return  
       # ==========================================================
# MAIN MESSAGE HANDLER
# ==========================================================


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    user_id = update.effective_user.id


    text = update.message.text.strip()



    # ==================================================
    # MENU BUTTONS
    # ==================================================


    if text == "⚙️ تنظیمات":


        await settings_command(
            update,
            context
        )

        return



    if text == "📚 تاریخچه":


        await history_command(
            update,
            context
        )

        return



    if text == "👤 پروفایل":


        await me_command(
            update,
            context
        )

        return



    if text == "❓ راهنما":


        await help_command(
            update,
            context
        )

        return



    # ==================================================
    # VALIDATE URL
    # ==================================================


    if not is_youtube_url(text):


        await safe_reply(

            update,

            "❌ لطفاً یک لینک معتبر یوتیوب ارسال کنید."

        )

        return



    url = text



    # ==================================================
    # STATUS MESSAGE
    # ==================================================


    status_message = await update.message.reply_text(

        "📥 در حال دریافت اطلاعات ویدیو..."

    )



    try:


        # ==============================================
        # USER SETTINGS
        # ==============================================


        user = users.get_user(

            user_id

        )


        if not user:

            user = {}



        language = user.get(

            "language",

            "Persian"

        )



        summary_type = user.get(

            "summary_type",

            "detailed"

        )



        # ==============================================
        # CACHE CHECK
        # ==============================================


        await safe_edit(

            status_message,

            "🔍 بررسی کش..."

        )



        cached = cache.get(

            url,

            language,

            summary_type

        )



        if cached:


            await delete_message_safe(

                status_message

            )



            await send_long_message(

                update,

                cached

            )


            return



        # ==============================================
        # VIDEO INFO
        # ==============================================


        await safe_edit(

            status_message,

            "🎬 دریافت اطلاعات ویدیو..."

        )



        video = youtube_service.process(

            url

        )



        if not video:


            await safe_edit(

                status_message,

                "❌ دریافت اطلاعات ویدیو ناموفق بود."

            )



            return



        logger.info(

            f"Video loaded: {video.title}"

        )



        # ==============================================
        # TRANSCRIPT
        # ==============================================


        await safe_edit(

            status_message,

            "📝 استخراج زیرنویس..."

        )



        transcript = video.transcript



        if not transcript:


            await safe_edit(

                status_message,

                "❌ زیرنویس یافت نشد."

            )


            return



        logger.info(

            f"Transcript size: {len(transcript)}"

        )
                # ==============================================
        # AI SUMMARY
        # ==============================================

        await safe_edit(
            status_message,
            "🤖 هوش مصنوعی در حال تحلیل..."
        )

        summary = summarizer_service.summarize(
            transcript=transcript,
            language=language,
            summary_type=summary_type
        )

        if not summary:

            await safe_edit(
                status_message,
                "❌ خلاصه تولید نشد."
            )

            return

        logger.info("Summary generated")

        # ==============================================
        # FORMAT OUTPUT
        # ==============================================

        await safe_edit(
            status_message,
            "📄 آماده‌سازی خروجی..."
        )

        result = format_summary(
            video,
            summary
        )

        # ==============================================
        # SAVE HISTORY
        # ==============================================

        try:

            history.add(
                user_id=user_id,
                title=video.title,
                channel=video.channel,
                url=video.url,
                summary=result
            )

        except Exception as e:

            logger.error(
                f"History save failed: {e}"
            )

        # ==============================================
        # SAVE CACHE
        # ==============================================

        try:

            cache.set(
                url=url,
                language=language,
                summary_type=summary_type,
                summary=result
            )

        except Exception as e:

            logger.error(
                f"Cache save failed: {e}"
            )

        # ==============================================
        # UPDATE USER STATS
        # ==============================================

        try:

            users.increment_requests(
                user_id
            )

        except Exception:

            pass

        # ==============================================
        # FINISHED
        # ==============================================

        await safe_edit(
            status_message,
            "✅ خلاصه آماده شد."
        )

        await asyncio.sleep(0.5)

        await delete_message_safe(
            status_message
        )

        await send_long_message(
            update,
            result
        )

    except Exception as e:

        logger.exception(
            "Processing error"
        )

        try:

            await safe_edit(
                status_message,
                "❌ خطایی رخ داد."
            )

        except Exception:
            pass

        await safe_reply(
            update,
            f"❌ {str(e)}"
        )
        # ==========================================================
# FORMAT SUMMARY
# ==========================================================


def format_summary(
    video,
    summary
):

    # ------------------------------------------
    # None Protection
    # ------------------------------------------

    if summary is None:

        summary = {}



    overview = summary.get(

        "overview",

        "خلاصه‌ای تولید نشد."

    )



    key_points = summary.get(

        "key_points",

        []

    )



    important_terms = summary.get(

        "important_terms",

        []

    )



    tools = summary.get(

        "tools",

        []

    )



    resources = summary.get(

        "resources",

        []

    )



    takeaway = summary.get(

        "final_takeaway",

        ""

    )



    text = f"""
🎬 {video.title}

📺 {video.channel}

⏱ {video.duration}

━━━━━━━━━━━━━━━━━━

🧠 خلاصه

{overview}

"""



    # ------------------------------------------
    # Key Points
    # ------------------------------------------

    if key_points:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "📌 نکات مهم\n\n"



        for point in key_points:

            text += f"• {point}\n"



    # ------------------------------------------
    # Important Terms
    # ------------------------------------------

    if important_terms:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "📚 اصطلاحات مهم\n\n"



        for term in important_terms:

            text += f"• {term}\n"



    # ------------------------------------------
    # Tools
    # ------------------------------------------

    if tools:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "🛠 ابزارها\n\n"



        for tool in tools:

            text += f"• {tool}\n"



    # ------------------------------------------
    # Resources
    # ------------------------------------------

    if resources:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "🔗 منابع\n\n"



        for item in resources:

            text += f"• {item}\n"



    # ------------------------------------------
    # Takeaway
    # ------------------------------------------

    if takeaway:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "🎯 نتیجه نهایی\n\n"

        text += takeaway



    text += "\n\n━━━━━━━━━━━━━━━━━━\n"

    text += "🤖 Powered by AI"



    return text
    # ==========================================================
# HELPER FUNCTIONS
# ==========================================================

from telegram.constants import ChatAction


async def typing_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    نمایش وضعیت تایپ کردن ربات
    """

    try:

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )

    except Exception:
        pass


# ==========================================================
# UPDATE STATUS MESSAGE
# ==========================================================

async def update_status(
    message,
    text: str
):
    """
    تغییر متن پیام وضعیت
    """

    try:

        await message.edit_text(text)

    except Exception:

        pass


# ==========================================================
# SAFE DELETE
# ==========================================================

async def safe_delete(
    message
):
    """
    حذف امن پیام
    """

    try:

        await message.delete()

    except Exception:

        pass


# ==========================================================
# SAFE REPLY
# ==========================================================

async def safe_reply(
    update,
    text,
    **kwargs
):
    """
    ارسال امن پیام
    """

    try:

        return await update.effective_message.reply_text(
            text,
            **kwargs
        )

    except Exception as e:

        logger.error(
            f"Reply error: {e}"
        )


# ==========================================================
# SAFE EDIT
# ==========================================================

async def safe_edit(
    message,
    text,
    **kwargs
):
    """
    ویرایش امن پیام
    """

    try:

        await message.edit_text(
            text,
            **kwargs
        )

    except Exception as e:

        logger.error(
            f"Edit error: {e}"
        )


# ==========================================================
# DELETE MESSAGE SAFE
# ==========================================================

async def delete_message_safe(
    message
):
    """
    حذف امن پیام
    """

    try:

        await message.delete()

    except Exception:

        pass


# ==========================================================
# SEND LONG MESSAGE
# ==========================================================

async def send_long_message(
    update,
    text
):
    """
    اگر متن بیشتر از محدودیت تلگرام باشد،
    آن را چند قسمت می‌کند.
    """

    LIMIT = 4000

    if len(text) <= LIMIT:

        await safe_reply(
            update,
            text
        )

        return

    start = 0

    while start < len(text):

        part = text[start:start + LIMIT]

        await safe_reply(
            update,
            part
        )

        start += LIMIT


# ==========================================================
# END OF FILE
# ==========================================================