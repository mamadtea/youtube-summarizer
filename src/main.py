from telegram import BotCommand 
from telegram.ext import ( 
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from src.config.settings import BOT_TOKEN 
from src.bot.handlers import (
    start,
    handle_message,
    language_callback,
    summary_type_callback,
    settings_command,
    settings_callback,
    history_command,
    me_command,
    help_command,
    summary_callback,
)
from src.bot.error_handler import error_handler 
from src.bot.handlers.message import cache
from src.database import users, history
from src.core.logger import setup_logger 

logger = setup_logger()


async def post_init(application: Application) -> None:
    # Initialize all SQLite Database Connections
    await cache.init()
    await users.init()
    await history.init()
    
    # Register Telegram UI Commands
    await application.bot.set_my_commands( 
        [
            BotCommand("start", "🚀 شروع ربات"),
            BotCommand("help", "❓ راهنما"),
            BotCommand("settings", "⚙️ تنظیمات"),
            BotCommand("history", "📚 تاریخچه خلاصه‌ها"),
            BotCommand("me", "👤 پروفایل"),
        ] 
    )
    logger.info("Telegram commands registered & All databases initialized.")


def main() -> None:
    logger.info("Bot started")

    application = ( 
        Application.builder() 
        .token(BOT_TOKEN) 
        .post_init(post_init) 
        .build() 
    ) 

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("me", me_command))

    application.add_handler(CallbackQueryHandler(language_callback, pattern=r"^language:"))
    application.add_handler(CallbackQueryHandler(summary_type_callback, pattern=r"^summary:"))
    application.add_handler(CallbackQueryHandler(settings_callback, pattern=r"^settings:"))
    application.add_handler(CallbackQueryHandler(summary_callback, pattern=r"^(export_|resummarize:|share:)"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(error_handler)

    logger.info("🤖 YouTube Summarizer Bot is running...")

    try:
        application.run_polling()
    finally:
        pass


if __name__ == "__main__":

    main()