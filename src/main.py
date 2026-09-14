import sys

if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from telegram import BotCommand
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.bot.error_handler import error_handler
from src.bot.handlers import (
    handle_message,
    help_command,
    history_command,
    language_callback,
    me_command,
    plans_command,
    settings_callback,
    settings_command,
    start,
    subscription_callback,
    summary_callback,
    summary_type_callback,
)
from src.bot.handlers.message import cache
from src.bot.handlers.payment import (
    handle_receipt,
    payment_callback,
)
from src.config.settings import BOT_TOKEN
from src.core.logger import setup_logger
from src.database import history, payments, subscriptions, users

logger = setup_logger()


async def post_init(application: Application) -> None:
    """
    Initialize databases, cache and Telegram bot commands.
    """

    await cache.init()
    await users.init()
    await history.init()
    await subscriptions.init()
    await payments.init()

    await application.bot.set_my_commands(
        [
            BotCommand("start", "🚀 شروع ربات"),
            BotCommand("help", "❓ راهنما"),
            BotCommand("settings", "⚙️ تنظیمات"),
            BotCommand("history", "📚 تاریخچه خلاصه‌ها"),
            BotCommand("me", "👤 پروفایل"),
            BotCommand("plans", "💳 خرید اشتراک"),
        ]
    )

    logger.info(
        "Telegram commands registered & All databases initialized."
    )


def main() -> None:
    """
    Start Telegram bot.
    """

    logger.info("Bot started")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # =========================================================
    # Commands
    # =========================================================

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("settings", settings_command)
    )

    application.add_handler(
        CommandHandler("history", history_command)
    )

    application.add_handler(
        CommandHandler("me", me_command)
    )

    application.add_handler(
        CommandHandler("plans", plans_command)
    )

    # =========================================================
    # Existing callbacks
    # =========================================================

    application.add_handler(
        CallbackQueryHandler(
            language_callback,
            pattern=r"^language:",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            summary_type_callback,
            pattern=r"^summary:",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            settings_callback,
            pattern=r"^settings:",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            summary_callback,
            pattern=r"^(export_|resummarize:|share:)",
        )
    )

    # =========================================================
    # Subscription callbacks
    # =========================================================

    application.add_handler(
        CallbackQueryHandler(
            subscription_callback,
            pattern=r"^subscription:",
        )
    )

    # =========================================================
    # Payment callbacks
    # =========================================================

    application.add_handler(
        CallbackQueryHandler(
            payment_callback,
            pattern=r"^payment:",
        )
    )

    # =========================================================
    # Receipt photos
    # =========================================================

    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            handle_receipt,
        )
    )

    # =========================================================
    # Text messages
    # =========================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    # =========================================================
    # Error handler
    # =========================================================

    application.add_error_handler(
        error_handler
    )

    logger.info(
        "🤖 YouTube Summarizer Bot is running..."
    )

    try:
        application.run_polling()
    finally:
        pass


if __name__ == "__main__":
    main()