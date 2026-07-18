from telegram import Update
from telegram.ext import ContextTypes

from src.database import users
from src.database import history

from src.bot.keyboards import (
    language_keyboard,
    summary_type_keyboard,
)

from src.bot.handlers.helpers import safe_edit


# =====================================================
# LANGUAGE CALLBACK
# =====================================================

async def language_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    language = query.data.split(":")[1]

    users.set_language(
        user_id,
        language
    )

    await safe_edit(
        query.message,
        f"✅ زبان روی **{language}** تنظیم شد."
    )


# =====================================================
# SUMMARY TYPE CALLBACK
# =====================================================

async def summary_type_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    summary_type = query.data.split(":")[1]

    users.set_summary_type(
        user_id,
        summary_type
    )

    await safe_edit(
        query.message,
        f"✅ نوع خلاصه روی **{summary_type}** تنظیم شد."
    )


# =====================================================
# SETTINGS CALLBACK
# =====================================================

async def settings_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    action = query.data.split(":")[1]

    # ==========================================
    # CHANGE LANGUAGE
    # ==========================================

    if action == "language":

        await safe_edit(

            query.message,

            "🌍 زبان خلاصه را انتخاب کنید:",

            reply_markup=language_keyboard()

        )

        return

    # ==========================================
    # CHANGE SUMMARY TYPE
    # ==========================================

    if action == "summary":

        await safe_edit(

            query.message,

            "📝 نوع خلاصه را انتخاب کنید:",

            reply_markup=summary_type_keyboard()

        )

        return

    # ==========================================
    # PROFILE
    # ==========================================

    if action == "profile":

        user = users.get_user(
            user_id
        )

        total = history.count(
            user_id
        )

        text = f"""
👤 پروفایل

━━━━━━━━━━━━━━

🆔 شناسه:
{user_id}

🌍 زبان:
{user["language"]}

📝 نوع خلاصه:
{user["summary_type"]}

📊 تعداد درخواست‌ها:
{user["requests"]}

📚 تعداد خلاصه‌ها:
{total}
"""

        await safe_edit(
            query.message,
            text
        )

        return

    # ==========================================
    # HISTORY
    # ==========================================

    if action == "history":

        items = history.get_history(
            user_id
        )

        if not items:

            await safe_edit(
                query.message,
                "📭 هنوز خلاصه‌ای ذخیره نشده است."
            )

            return

        text = "📚 تاریخچه خلاصه‌ها\n\n"

        for index, item in enumerate(
            items,
            start=1
        ):

            title = item[0]
            channel = item[1]
            created = item[2]

            text += (
                f"{index}. 🎬 {title}\n"
                f"📺 {channel}\n"
                f"🕒 {created}\n\n"
            )

        if len(text) > 4000:
            text = text[:4000] + "\n..."

        await safe_edit(
            query.message,
            text
        )

        return
    from telegram import Update
from telegram.ext import ContextTypes

from src.services.export import (
    create_pdf,
    create_txt,
    create_markdown
)



async def summary_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    data = query.data


    if data.startswith(
        "export_pdf:"
    ):

        await export_pdf_handler(
            query,
            context
        )


    elif data.startswith(
        "export_txt:"
    ):

        await export_txt_handler(
            query,
            context
        )


    elif data.startswith(
        "export_md:"
    ):

        await export_markdown_handler(
            query,
            context
        )


    elif data.startswith(
        "share:"
    ):

        await share_handler(
            query
        )



async def export_pdf_handler(
    query,
    context
):

    summary = context.user_data.get(
        "last_summary"
    )


    if not summary:

        await query.message.reply_text(
            "❌ خلاصه‌ای پیدا نشد."
        )

        return


    file_path = create_pdf(
        summary
    )


    await query.message.reply_document(
        document=open(
            file_path,
            "rb"
        )
    )



async def export_txt_handler(
    query,
    context
):

    summary = context.user_data.get(
        "last_summary"
    )


    if not summary:

        return


    file_path = create_txt(
        summary
    )


    await query.message.reply_document(
        document=open(
            file_path,
            "rb"
        )
    )



async def export_markdown_handler(
    query,
    context
):

    summary = context.user_data.get(
        "last_summary"
    )


    if not summary:

        return


    file_path = create_markdown(
        summary
    )


    await query.message.reply_document(
        document=open(
            file_path,
            "rb"
        )
    )



async def share_handler(
    query
):

    text = (
        "📺 خلاصه ویدیو ساخته شد.\n\n"
        "با YouTube Summarizer"
    )


    await query.message.reply_text(
        text
    )