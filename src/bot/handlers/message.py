
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.handlers.formatter import format_summary
from src.bot.handlers.helpers import StatusMessage
from src.bot.keyboards import summary_keyboard
from src.core.logger import setup_logger
from src.database import history, subscriptions, users
from src.services.ai.summarizer import SummarizerService
from src.services.cache.summary_cache import SummaryCache
from src.services.dictionary.service import enrich_terms_with_definitions
from src.services.youtube.service import YouTubeService

logger = setup_logger()

youtube_service = YouTubeService()
summarizer_service = SummarizerService()
cache = SummaryCache()


class ProcessingError(Exception):
    """Expected error during YouTube processing."""


def is_youtube_url(url: str) -> bool:
    return (
        "youtube.com" in url
        or "youtu.be" in url
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()
    user_id = update.effective_user.id

    if not is_youtube_url(url):
        await update.message.reply_text(
            "❌ لطفاً یک لینک معتبر YouTube ارسال کنید."
        )
        return

    user = await users.get_user(user_id)

    language = user.get(
        "language",
        "Persian",
    )

    summary_type = user.get(
        "summary_type",
        "complete",
    )

    subscription = await subscriptions.get_active(
        user_id
    )

    using_subscription = bool(
        subscription
        and subscription.get(
            "credits_remaining",
            0,
        ) > 0
    )

    if (
        not using_subscription
        and not await users.has_free_today(user_id)
    ):
        await update.message.reply_text(
            "❌ سهم رایگان امروز شما استفاده شده است.\n\n"
            "برای ادامه خلاصه‌سازی، لطفاً یکی از "
            "پلن‌های اشتراک را خریداری کنید."
        )
        return

    initial_msg = await update.message.reply_text(
        "🔗 دریافت اطلاعات ویدیو..."
    )

    status = StatusMessage(initial_msg)

    try:
        cached = await cache.get(
            url,
            language,
            summary_type,
        )

        video_data = None

        if cached:
            logger.info(
                "Cache HIT for URL: %s",
                url,
            )

            summary = cached

            await status.update(
                "⚡ خلاصه از حافظه دریافت شد..."
            )

        else:
            logger.info(
                "Cache MISS for URL: %s",
                url,
            )

            await status.update(
                "📺 دریافت اطلاعات ویدیو..."
            )

            video_obj = await asyncio.to_thread(
                youtube_service.process,
                url,
            )

            if not video_obj:
                raise ProcessingError(
                    "دریافت اطلاعات ویدیو ناموفق بود."
                )

            if not video_obj.transcript:
                raise ProcessingError(
                    "متنی برای خلاصه‌سازی این ویدیو پیدا نشد."
                )

            video_data = {
                "id": getattr(
                    video_obj,
                    "id",
                    "unknown",
                ),
                "title": getattr(
                    video_obj,
                    "title",
                    "YouTube Video",
                ),
                "channel": getattr(
                    video_obj,
                    "channel",
                    getattr(
                        video_obj,
                        "uploader",
                        "Unknown",
                    ),
                ),
            }

            await status.update(
                "🤖 تحلیل با هوش مصنوعی..."
            )

            try:
                summary = await asyncio.to_thread(
                    summarizer_service.summarize,
                    transcript=video_obj.transcript,
                    language=language,
                    summary_type=summary_type,
                    context_hint="a YouTube video transcript",
                )
            except Exception as exc:
                logger.exception(
                    "AI summarization failed"
                )

                raise ProcessingError(
                    f"خطا در هوش مصنوعی:\n{exc}"
                ) from exc

            if not isinstance(summary, dict):
                raise ProcessingError(
                    "هوش مصنوعی نتیجه معتبری برنگرداند."
                )

            if not summary.get("summary"):
                raise ProcessingError(
                    "هوش مصنوعی خلاصه معتبری تولید نکرد."
                )

            logger.info(
                "Summary completed by AI"
            )

            await cache.set(
                url,
                language,
                summary_type,
                summary,
            )

            await history.add(
                user_id=user_id,
                video_id=video_data["id"],
                title=video_data["title"],
                channel=video_data["channel"],
            )

        if using_subscription:
            consumed = await subscriptions.consume_credit(
                user_id
            )

            if not consumed:
                raise ProcessingError(
                    "خلاصه آماده شد، اما در ثبت اعتبار مشکلی رخ داد."
                )

        else:
            consumed = await users.consume_free_today(
                user_id
            )

            if not consumed:
                raise ProcessingError(
                    "سهم رایگان امروز شما قبلاً استفاده شده است."
                )

        await users.increase_requests(
            user_id
        )

        context.user_data["last_summary"] = summary
        context.user_data["last_url"] = url

        if (
            summary_type == "educational"
            and isinstance(summary, dict)
            and summary.get("terms")
        ):
            await status.update(
                "📚 یافتن معنی اصطلاحات از دیکشنری..."
            )

            summary["terms"] = (
                await enrich_terms_with_definitions(
                    summary["terms"]
                )
            )

        formatted_summary = format_summary(
            summary
        )

        if using_subscription:
            subscription = await subscriptions.get_active(
                user_id
            )

            if subscription:
                remaining = subscription.get(
                    "credits_remaining",
                    0,
                )

                formatted_summary += (
                    "\n\n💳 اعتبار باقی‌مانده: "
                    f"{remaining}"
                )
        else:
            formatted_summary += (
                "\n\n🆓 سهم رایگان امروز شما استفاده شد."
            )

        video_id = (
            video_data.get(
                "id",
                "cached",
            )
            if video_data
            else "cached"
        )

        await status.update(
            formatted_summary,
            reply_markup=summary_keyboard(
                video_id
            ),
        )

    except ProcessingError as exc:
        logger.warning(
            "Processing failed: %s",
            exc,
        )

        await status.update(
            f"❌ خطا در پردازش:\n{exc}"
        )

