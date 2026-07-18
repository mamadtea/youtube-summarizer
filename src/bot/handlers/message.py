import logging


from telegram import Update
from telegram.ext import ContextTypes


from src.services.youtube.service import YouTubeService
from src.services.ai.summarizer import SummarizerService
from src.services.cache.summary_cache import SummaryCache


from src.database import users
from src.database import history


from src.bot.keyboards import summary_keyboard



logger = logging.getLogger(
    "youtube_summarizer"
)



# ==============================
# Services
# ==============================


youtube_service = YouTubeService()

summarizer_service = SummarizerService()

cache = SummaryCache()



# ==============================
# Handle Message
# ==============================


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    url = update.message.text.strip()


    user_id = (
        update.effective_user.id
    )



    status = await update.message.reply_text(
        "🎬 دریافت لینک ویدیو..."
    )



    try:


        # --------------------------
        # User Settings
        # --------------------------


        user = users.get_user(
            user_id
        )


        language = user.get(
            "language",
            "Persian"
        )


        summary_type = user.get(
            "summary_type",
            "detailed"
        )



        # --------------------------
        # Check Cache
        # --------------------------


        cached = cache.get(
            url,
            language,
            summary_type
        )



        video = None



        if cached:


            summary = cached


            await status.edit_text(
                "⚡ خلاصه از حافظه دریافت شد"
            )



        else:



            # --------------------------
            # Youtube Processing
            # --------------------------


            await status.edit_text(
                "📺 دریافت اطلاعات ویدیو..."
            )


            video = youtube_service.process(
                url
            )



            await status.edit_text(
                "📝 استخراج زیرنویس..."
            )



            if not video.transcript:


                await status.edit_text(
                    "❌ زیرنویس این ویدیو پیدا نشد"
                )

                return



            # --------------------------
            # AI Summary
            # --------------------------


            await status.edit_text(
                "🤖 تحلیل با هوش مصنوعی..."
            )



            summary = summarizer_service.summarize(

                transcript=video.transcript,

                language=language,

                summary_type=summary_type

            )



            # --------------------------
            # Save Cache
            # --------------------------


            cache.set(

                url,

                language,

                summary_type,

                summary

            )



            # --------------------------
            # Save History
            # --------------------------


            history.add(

                user_id=user_id,

                video_id=video.id,

                title=video.title,

                channel=video.channel

            )



            users.increase_requests(

                user_id

            )




        # --------------------------
        # Save Last Summary
        # --------------------------


        context.user_data[

            "last_summary"

        ] = summary



        context.user_data[

            "last_url"

        ] = url




        # --------------------------
        # Format Output
        # --------------------------


        formatted_summary = format_summary(
            summary
        )



        await status.delete()



        await update.message.reply_text(

            formatted_summary,

            reply_markup=summary_keyboard(

                video.id

                if video

                else "cached"

            )

        )



    except Exception as e:


        logger.exception(
            "Processing error"
        )


        await status.edit_text(

            f"❌ خطا در پردازش:\n{str(e)}"

        )




# ==============================
# Formatter
# ==============================


def format_summary(
    summary: dict
):


    text = "🎬 خلاصه ویدیو\n\n"


    text += "━━━━━━━━━━━━━━\n\n"



    text += summary.get(

        "summary",

        ""

    )



    text += "\n\n📌 نکات کلیدی:\n"



    for point in summary.get(

        "key_points",

        []

    ):


        text += f"\n• {point}"



    return text