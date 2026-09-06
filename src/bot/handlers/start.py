from telegram import Update
from telegram.ext import ContextTypes

from src.database import users
from src.bot.keyboards import settings_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    await users.create_if_not_exists(user.id, user.first_name)

    text = (
        f"👋 سلام {user.first_name}\n\n"
        "به ربات خلاصه‌ساز هوشمند یوتیوب و اینستاگرام خوش آمدید.\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🎬 فقط لینک ویدیو را ارسال کنید.\n\n"
        "ربات به صورت خودکار:\n"
        "✅ اطلاعات ویدیو را دریافت می‌کند\n"
        "✅ زیرنویس/صدا را استخراج می‌کند\n"
        "✅ با هوش مصنوعی تحلیل می‌کند\n"
        "✅ خلاصه کامل تولید می‌کند\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "دستورات:\n"
        "/settings - تنظیمات\n"
        "/history - تاریخچه\n"
        "/me - پروفایل\n"
        "/help - راهنما"
    )

    await update.message.reply_text(text, reply_markup=settings_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📚 راهنما\n\n"
        "فقط لینک YouTube یا Instagram ارسال کنید.\n\n"
        "مثال یوتیوب:\n"
        "https://youtu.be/xxxx\n\n"
        "مثال اینستاگرام:\n"
        "https://www.instagram.com/reel/xxxx"
    )
    await update.message.reply_text(text)


async def me_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data = await users.get_user(user_id)

    type_names = {"brief": "کوتاه", "complete": "کامل", "educational": "آموزشی"}
    display_type = type_names.get(user_data['summary_type'], user_data['summary_type'])

    text = (
        "👤 پروفایل\n\n"
        f"🌍 زبان:\n{user_data['language']}\n\n"
        f"📝 نوع خلاصه:\n{display_type}\n\n"
        f"📊 تعداد درخواست:\n{user_data['requests']}"
    )

    await update.message.reply_text(text)


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("📚 برای مشاهده تاریخچه از دکمه History داخل Settings استفاده کنید.")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⚙ تنظیمات", reply_markup=settings_keyboard())