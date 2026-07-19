from telegram import InlineKeyboardButton, InlineKeyboardMarkup 
 

def settings_keyboard() -> InlineKeyboardMarkup:
    keyboard = [ 
        [
            InlineKeyboardButton("🌍 زبان", callback_data="settings:language"),
            InlineKeyboardButton("📝 نوع خلاصه", callback_data="settings:summary"),
        ],
        [
            InlineKeyboardButton("👤 پروفایل", callback_data="settings:profile"),
            InlineKeyboardButton("📚 تاریخچه", callback_data="settings:history"),
        ],
    ] 
    return InlineKeyboardMarkup(keyboard)


def language_keyboard() -> InlineKeyboardMarkup:
    keyboard = [ 
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data="language:Persian"),
            InlineKeyboardButton("🇬🇧 English", callback_data="language:English"),
        ],
        [ 
            InlineKeyboardButton("🔙 بازگشت", callback_data="settings:main"),
        ],
    ] 
    return InlineKeyboardMarkup(keyboard)


def summary_type_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [ 
            InlineKeyboardButton("📋 کوتاه", callback_data="summary:brief"),
        ],
        [
            InlineKeyboardButton("📖 کامل", callback_data="summary:complete"),
        ], 
        [
            InlineKeyboardButton("🎓 آموزشی", callback_data="summary:educational"),
        ],
        [ 
            InlineKeyboardButton("🔙 بازگشت", callback_data="settings:main"),
        ],
    ] 
    return InlineKeyboardMarkup(keyboard)


def summary_keyboard(video_id: str) -> InlineKeyboardMarkup:
    keyboard = [
        [ 
            InlineKeyboardButton("🔄 خلاصه مجدد", callback_data=f"resummarize:{video_id}"),
        ], 
        [
            InlineKeyboardButton("📄 Export PDF", callback_data=f"export_pdf:{video_id}"),
            InlineKeyboardButton("📝 Export TXT", callback_data=f"export_txt:{video_id}"),
        ], 
        [
            InlineKeyboardButton("📘 Export Markdown", callback_data=f"export_md:{video_id}"),
        ], 
        [
            InlineKeyboardButton("📤 اشتراک‌گذاری", callback_data=f"share:{video_id}"),
            InlineKeyboardButton("⚙ تنظیمات", callback_data="settings:main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)