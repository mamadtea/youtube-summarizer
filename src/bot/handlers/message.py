import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from src.services.youtube.service import YouTubeService
from src.services.ai.summarizer import SummarizerService
from src.services.cache.summary_cache import SummaryCache

from src.database import users, history

from src.bot.keyboards import summary_keyboard
from src.bot.handlers.formatter import format_summary
from src.bot.handlers.helpers import StatusMessage
from src.core.logger import setup_logger

logger = setup_logger()

youtube_service = YouTubeService()
summarizer_service = SummarizerService()
cache = SummaryCache()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()
    user_id = update.effective_user.id

    initial_msg = await update.message.reply_text("🎬 دریافت لینک ویدیو...")
    status = StatusMessage(initial_msg)

    try:
        user = await users.get_user(user_id)
        language = user.get("language", "Persian")
        summary_type = user.get("summary_type", "detailed")

        cached = await cache.get(url, language, summary_type)
        video = None

        if cached:
            logger.info(f"Cache HIT for URL: {url}")
            summary = cached
            await status.update("⚡ خلاصه از حافظه دریافت شد...")
        else:
            logger.info(f"Cache MISS for URL: {url}")
            
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
            logger.info("Summary completed by AI")

            await cache.set(url, language, summary_type, summary)

            await history.add(user_id=user_id, video_id=video.id, title=video.title, channel=video.channel)
            await users.increase_requests(user_id)

        context.user_data["last_summary"] = summary
        context.user_data["last_url"] = url

        formatted_summary = format_summary(summary)

        await status.update(
            formatted_summary,
            reply_markup=summary_keyboard(video.id if video else "cached")
        )

    except Exception as e:
        logger.exception("Processing error")
        try:
            await status.update(f"❌ خطا در پردازش:\n{str(e)}")
        except Exception:
            await update.message.reply_text(f"❌ خطا در پردازش:\n{str(e)}")