import os
import asyncio
import logging
from typing import Optional

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from src.database import users, history
from src.bot.keyboards import language_keyboard, summary_type_keyboard, summary_keyboard, settings_keyboard
from src.bot.handlers.helpers import safe_edit, StatusMessage
from src.bot.handlers.formatter import format_summary
from src.services.export import create_pdf, create_txt, create_markdown

from src.bot.handlers.message import youtube_service, summarizer_service, cache

logger = logging.getLogger("youtube_summarizer")


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = query.data.split(":")[1]

    await users.set_language(user_id, language)
    
    await safe_edit(
        query.message,
        f"✅ زبان روی **{language}** تنظیم شد.",
        reply_markup=settings_keyboard()
    )


async def summary_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    summary_type = query.data.split(":")[1]

    await users.set_summary_type(user_id, summary_type)
    
    # دیکشنری برای نمایش نام زیبای نوع خلاصه به کاربر
    type_names = {
        "brief": "کوتاه (Brief)",
        "complete": "کامل (Complete)",
        "educational": "آموزشی (Educational)"
    }
    display_name = type_names.get(summary_type, summary_type)
    
    await safe_edit(
        query.message,
        f"✅ نوع خلاصه روی **{display_name}** تنظیم شد.",
        reply_markup=settings_keyboard()
    )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data.split(":")[1]

    if action == "main":
        await safe_edit(query.message, "⚙ تنظیمات", reply_markup=settings_keyboard())
        return

    if action == "language":
        await safe_edit(query.message, "🌍 زبان خلاصه را انتخاب کنید:", reply_markup=language_keyboard())
        return

    if action == "summary":
        await safe_edit(query.message, "📝 نوع خلاصه را انتخاب کنید:", reply_markup=summary_type_keyboard())
        return

    if action == "profile":
        user = await users.get_user(user_id)
        total = await history.count(user_id)

        # نمایش نام زیبای نوع خلاصه در پروفایل
        type_names = {
            "brief": "کوتاه",
            "complete": "کامل",
            "educational": "آموزشی"
        }
        display_type = type_names.get(user['summary_type'], user['summary_type'])

        text = (
            "👤 پروفایل\n\n"
            "━━━━━━━━━━━━━━\n\n"
            f"🆔 شناسه:\n{user_id}\n\n"
            f"🌍 زبان:\n{user['language']}\n\n"
            f"📝 نوع خلاصه:\n{display_type}\n\n"
            f"📊 تعداد درخواست‌ها:\n{user['requests']}\n\n"
            f"📚 تعداد خلاصه‌ها:\n{total}"
        )

        await safe_edit(query.message, text, reply_markup=settings_keyboard())
        return

    if action == "history":
        items = await history.get_history(user_id)

        if not items:
            await safe_edit(query.message, "📭 هنوز خلاصه‌ای ذخیره نشده است.", reply_markup=settings_keyboard())
            return

        text = "📚 تاریخچه خلاصه‌ها\n\n"

        for index, item in enumerate(items, start=1):
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

        await safe_edit(query.message, text, reply_markup=settings_keyboard())
        return


async def resummarize_handler(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = context.user_data.get("last_url")
    if not url:
        await query.message.reply_text("❌ لینک ویدیو یافت نشد. لطفاً لینک را دوباره ارسال کنید.")
        return

    user_id = query.from_user.id
    status_msg = await query.message.reply_text("🔄 در حال خلاصه‌سازی مجدد...")
    status = StatusMessage(status_msg)

    try:
        user = await users.get_user(user_id)
        language = user.get("language", "Persian")
        summary_type = user.get("summary_type", "complete")

        await cache.delete(url, language, summary_type)

        await status.update("📺 دریافت اطلاعات ویدیو...")
        video = await asyncio.to_thread(youtube_service.process, url)

        await status.update("📝 استخراج زیرنویس...")

        if not video or not video.transcript:
            await status.update("❌ زیرنویس این ویدیو پیدا نشد")
            return

        await status.update("🤖 تحلیل با هوش مصنوعی...")

        summary = await asyncio.to_thread(
            summarizer_service.summarize,
            transcript=video.transcript,
            language=language,
            summary_type=summary_type
        )
        
        await cache.set(url, language, summary_type, summary)
        await history.add(user_id=user_id, video_id=video.id, title=video.title, channel=video.channel)
        await users.increase_requests(user_id)

        context.user_data["last_summary"] = summary
        context.user_data["last_url"] = url

        formatted_summary = format_summary(summary)

        await status.update(
            formatted_summary,
            reply_markup=summary_keyboard(video.id)
        )

    except Exception as e:
        logger.exception("Resummarize processing error")
        try:
            await status.update(f"❌ خطا در پردازش:\n{str(e)}")
        except Exception:
            await query.message.reply_text(f"❌ خطا در پردازش:\n{str(e)}")


async def _handle_export(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, export_type: str) -> None:
    summary = context.user_data.get("last_summary")
    
    if not summary:
        await query.message.reply_text("❌ خلاصه‌ای پیدا نشد. لطفاً ابتدا یک ویدیو را خلاصه کنید.")
        return

    file_path: Optional[str] = None
    
    try:
        if export_type == "pdf":
            file_path = await asyncio.to_thread(create_pdf, summary)
        elif export_type == "txt":
            file_path = await asyncio.to_thread(create_txt, summary)
        elif export_type == "md":
            file_path = await asyncio.to_thread(create_markdown, summary)
        else:
            return

        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as doc_file:
                await query.message.reply_document(document=doc_file)
            logger.info(f"Export completed: {export_type}")
        else:
            await query.message.reply_text("❌ خطا در ایجاد فایل.")

    except Exception as e:
        logger.exception(f"Error exporting to {export_type}")
        await query.message.reply_text(f"❌ خطا در تولید فایل: {str(e)}")
        
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                logger.error(f"Error deleting temp file {file_path}: {e}")


async def summary_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("resummarize:"):
        await resummarize_handler(query, context)
    elif data.startswith("export_pdf:"):
        await _handle_export(query, context, "pdf")
    elif data.startswith("export_txt:"):
        await _handle_export(query, context, "txt")
    elif data.startswith("export_md:"):
        await _handle_export(query, context, "md")
    elif data.startswith("share:"):
        await share_handler(query)


async def share_handler(query: CallbackQuery) -> None:
    text = (
        "📺 خلاصه ویدیو ساخته شد.\n\n"
        "با YouTube Summarizer"
    )
    await query.message.reply_text(text)