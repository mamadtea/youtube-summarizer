import os
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from src.services.youtube.service import YouTubeService
from src.services.instagram.service import instagram_service
from src.services.stt.suprsonic import transcribe_audio
from src.services.ai.summarizer import SummarizerService
from src.services.cache.summary_cache import SummaryCache
from src.services.dictionary.service import enrich_terms_with_definitions

from src.database import users, history

from src.bot.keyboards import summary_keyboard
from src.bot.handlers.formatter import format_summary
from src.bot.handlers.helpers import StatusMessage
from src.core.logger import setup_logger

logger = setup_logger()

youtube_service = YouTubeService()
summarizer_service = SummarizerService()
cache = SummaryCache()

def detect_platform(url: str) -> str:
    if "instagram.com" in url or "instagr.am" in url:
        return "instagram"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    return "unknown"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()
    user_id = update.effective_user.id
    
    platform = detect_platform(url)
    if platform == "unknown":
        await update.message.reply_text("❌ لطفاً فقط لینک یوتیوب یا اینستاگرام ارسال کنید.")
        return

    initial_msg = await update.message.reply_text(f"🔗 دریافت لینک {platform.capitalize()}...")
    status = StatusMessage(initial_msg)

    try:
        user = await users.get_user(user_id)
        language = user.get("language", "Persian")
        summary_type = user.get("summary_type", "complete")
        
        stt_lang = "fa" if language == "Persian" else "en"

        cached = await cache.get(url, language, summary_type)
        video_data = None

        if cached:
            logger.info(f"Cache HIT for URL: {url}")
            summary = cached
            await status.update("⚡ خلاصه از حافظه دریافت شد...")
        else:
            logger.info(f"Cache MISS for URL: {url}")
            
            transcript_text = ""
            context_hint = "a YouTube video transcript"
            
            if platform == "instagram":
                await status.update("📺 دریافت اطلاعات پست اینستاگرام...")
                ig_info = await asyncio.to_thread(instagram_service.get_info, url)
                
                if not ig_info:
                    await status.update("❌ خطا در دریافت اطلاعات اینستاگرام.")
                    return
                    
                video_data = ig_info # این یک دیکشنری است
                context_hint = "an Instagram reel/post"
                
                if ig_info.get("caption"):
                    transcript_text += "Caption:\n" + ig_info["caption"] + "\n\n"
                
                await status.update("🎙 دانلود صدای پست...")
                audio_path = await asyncio.to_thread(instagram_service.download_audio, url, ig_info["id"])
                
                if audio_path:
                    try:
                        await status.update("✍️ تبدیل صدا به متن توسط هوش مصنوعی...")
                        audio_text = await transcribe_audio(audio_path, language=stt_lang)
                        if audio_text:
                            transcript_text += "Audio Transcription:\n" + audio_text
                    finally:
                        if os.path.exists(audio_path):
                            os.remove(audio_path)
                            
            elif platform == "youtube":
                await status.update("📺 دریافت اطلاعات ویدیو...")
                video_obj = await asyncio.to_thread(youtube_service.process, url)
                
                if video_obj and video_obj.transcript:
                    transcript_text = video_obj.transcript
                    # تبدیل آبجکت Video به دیکشنری برای یکپارچگی با اینستاگرام
                    video_data = {
                        "id": getattr(video_obj, "id", "unknown"),
                        "title": getattr(video_obj, "title", "YouTube Video"),
                        "channel": getattr(video_obj, "channel", getattr(video_obj, "uploader", "Unknown"))
                    }

            if not transcript_text.strip():
                await status.update("❌ متنی برای خلاصه‌سازی در این پست یافت نشد.")
                return

            await status.update("🤖 تحلیل با هوش مصنوعی...")

            summary = await asyncio.to_thread(
                summarizer_service.summarize,
                transcript=transcript_text,
                language=language,
                summary_type=summary_type,
                context_hint=context_hint
            )
            logger.info("Summary completed by AI")

            await cache.set(url, language, summary_type, summary)

            await history.add(
                user_id=user_id, 
                video_id=video_data.get("id", "unknown"), 
                title=video_data.get("title", "Post"), 
                channel=video_data.get("channel", video_data.get("uploader", "Unknown"))
            )
            await users.increase_requests(user_id)

        context.user_data["last_summary"] = summary
        context.user_data["last_url"] = url

        if summary_type == "educational" and isinstance(summary, dict) and summary.get("terms"):
            try:
                await status.update("📚 یافتن معنی اصطلاحات از دیکشنری...")
                summary["terms"] = await enrich_terms_with_definitions(summary["terms"])
            except Exception as e:
                logger.error(f"Failed to enrich terms via API: {e}")

        formatted_summary = format_summary(summary)

        await status.update(
            formatted_summary,
            reply_markup=summary_keyboard(video_data.get("id", "cached") if video_data else "cached")
        )

    except Exception as e:
        logger.exception("Processing error")
        try:
            await status.update(f"❌ خطا در پردازش:\n{str(e)}")
        except Exception:
            await update.message.reply_text(f"❌ خطا در پردازش:\n{str(e)}")