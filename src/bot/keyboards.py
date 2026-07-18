from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ==========================================
# LANGUAGE KEYBOARD
# ==========================================

def language_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "🇮🇷 فارسی",
                callback_data="language:Persian"
            ),

            InlineKeyboardButton(
                "🇺🇸 English",
                callback_data="language:English"
            )
        ],

        [
            InlineKeyboardButton(
                "🇸🇦 العربية",
                callback_data="language:Arabic"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)


# ==========================================
# SUMMARY TYPE KEYBOARD
# ==========================================

def summary_type_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "⚡ کوتاه",
                callback_data="summary:short"
            )
        ],

        [
            InlineKeyboardButton(
                "📄 معمولی",
                callback_data="summary:medium"
            )
        ],

        [
            InlineKeyboardButton(
                "📚 کامل",
                callback_data="summary:detailed"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)


# ==========================================
# SETTINGS KEYBOARD
# ==========================================

def settings_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "🌍 تغییر زبان",
                callback_data="settings:language"
            )
        ],

        [
            InlineKeyboardButton(
                "📝 نوع خلاصه",
                callback_data="settings:summary"
            )
        ],

        [
            InlineKeyboardButton(
                "👤 پروفایل",
                callback_data="settings:profile"
            )
        ],

        [
            InlineKeyboardButton(
                "📚 تاریخچه",
                callback_data="settings:history"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)





def summary_keyboard(
    video_id: str
):

    keyboard = [

        [
            InlineKeyboardButton(
                "🔄 خلاصه مجدد",
                callback_data=f"resummarize:{video_id}"
            )
        ],

        [
            InlineKeyboardButton(
                "📄 PDF",
                callback_data=f"export_pdf:{video_id}"
            ),

            InlineKeyboardButton(
                "📝 TXT",
                callback_data=f"export_txt:{video_id}"
            )
        ],

        [
            InlineKeyboardButton(
                "📘 Markdown",
                callback_data=f"export_md:{video_id}"
            )
        ],

        [
            InlineKeyboardButton(
                "📤 Share",
                callback_data=f"share:{video_id}"
            )
        ],

        [
            InlineKeyboardButton(
                "⚙ Settings",
                callback_data="settings:main"
            )
        ]

    ]


    return InlineKeyboardMarkup(
        keyboard
    )