from telegram import Update
from telegram.ext import ContextTypes

from src.database import users
from src.bot.keyboards import settings_keyboard


# ==========================================
# START
# ==========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    users.create_if_not_exists(
        user.id,
        user.first_name
    )

    text = f"""
👋 سلام {user.first_name}

به ربات خلاصه‌ساز هوشمند یوتیوب خوش آمدید.

━━━━━━━━━━━━━━━━━━

🎬 فقط لینک ویدیو را ارسال کنید.

ربات به صورت خودکار:

✅ اطلاعات ویدیو را دریافت می‌کند
✅ زیرنویس را استخراج می‌کند
✅ با هوش مصنوعی تحلیل می‌کند
✅ خلاصه کامل تولید می‌کند

━━━━━━━━━━━━━━━━━━

دستورات:

/settings
/history
/me
/help
"""

    await update.message.reply_text(
        text,
        reply_markup=settings_keyboard()
    )


# ==========================================
# HELP
# ==========================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = """
📚 راهنما

فقط لینک YouTube ارسال کنید.

مثال:

https://youtu.be/xxxx

یا

https://youtube.com/watch?v=xxxx
"""

    await update.message.reply_text(text)


# ==========================================
# PROFILE
# ==========================================

async def me_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = users.get_user(
        update.effective_user.id
    )

    text = f"""
👤 پروفایل

🌍 زبان:
{user["language"]}

📝 نوع خلاصه:
{user["summary_type"]}

📊 تعداد درخواست:
{user["requests"]}
"""

    await update.message.reply_text(text)


# ==========================================
# HISTORY
# ==========================================

async def history_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "📚 برای مشاهده تاریخچه از دکمه History داخل Settings استفاده کنید."
    )


# ==========================================
# SETTINGS
# ==========================================

async def settings_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "⚙ تنظیمات",
        reply_markup=settings_keyboard()
    )