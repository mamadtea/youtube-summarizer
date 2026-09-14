import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.database import payments
from src.database.subscriptions import PLANS

PAYMENT_CARD_NUMBER = os.getenv("PAYMENT_CARD_NUMBER", "")
PAYMENT_CARD_NAME = os.getenv("PAYMENT_CARD_NAME", "")

# قیمت‌ها را فعلاً اینجا مشخص می‌کنیم.
# بعداً اگر خواستی از config/settings منتقلش می‌کنیم.
PLAN_PRICES = {
    "basic": 99000,
    "pro": 249000,
    "premium": 599000,
}


async def plans_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show available subscription plans."""

    keyboard = [
        [
            InlineKeyboardButton(
                "🟢 Basic - 30 خلاصه",
                callback_data="subscription:basic",
            )
        ],
        [
            InlineKeyboardButton(
                "🔵 Pro - 100 خلاصه",
                callback_data="subscription:pro",
            )
        ],
        [
            InlineKeyboardButton(
                "🟣 Premium - 300 خلاصه",
                callback_data="subscription:premium",
            )
        ],
    ]

    text = (
        "💳 <b>پلن‌های اشتراک</b>\n\n"
        "با خرید اشتراک می‌توانید از اعتبار خلاصه‌سازی "
        "استفاده کنید.\n\n"
        "🟢 <b>Basic</b>\n"
        "30 خلاصه — 30 روز\n\n"
        "🔵 <b>Pro</b>\n"
        "100 خلاصه — 30 روز\n\n"
        "🟣 <b>Premium</b>\n"
        "300 خلاصه — 30 روز\n\n"
        "👇 پلن موردنظر خود را انتخاب کنید:"
    )

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


async def subscription_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle subscription plan selection."""

    query = update.callback_query

    await query.answer()

    data = query.data or ""

    if not data.startswith("subscription:"):
        return

    plan = data.split(":", 1)[1]

    # -------------------------
    # Back to plans
    # -------------------------

    if plan == "back":
        keyboard = [
            [
                InlineKeyboardButton(
                    "🟢 Basic - 30 خلاصه",
                    callback_data="subscription:basic",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔵 Pro - 100 خلاصه",
                    callback_data="subscription:pro",
                )
            ],
            [
                InlineKeyboardButton(
                    "🟣 Premium - 300 خلاصه",
                    callback_data="subscription:premium",
                )
            ],
        ]

        await query.edit_message_text(
            "💳 <b>پلن‌های اشتراک</b>\n\n"
            "پلن موردنظر خود را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
        return

    # -------------------------
    # Validate plan
    # -------------------------

    if plan not in PLANS:
        await query.edit_message_text(
            "❌ پلن انتخاب‌شده معتبر نیست."
        )
        return

    plan_data = PLANS[plan]
    amount = PLAN_PRICES[plan]

    user_id = update.effective_user.id

    # -------------------------
    # Create payment
    # -------------------------

    payment = await payments.create_payment(
        user_id=user_id,
        plan=plan,
        amount=amount,
    )

    payment_id = payment["id"]

    # -------------------------
    # Payment information
    # -------------------------

    card_number = PAYMENT_CARD_NUMBER or "هنوز تنظیم نشده"
    card_name = PAYMENT_CARD_NAME or "هنوز تنظیم نشده"

    text = (
        f"💳 <b>خرید اشتراک {plan_data['name']}</b>\n\n"
        f"📊 اعتبار: <b>{plan_data['credits']} خلاصه</b>\n"
        "📅 مدت اعتبار: <b>30 روز</b>\n"
        f"💰 مبلغ: <b>{amount:,} تومان</b>\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🏦 <b>اطلاعات پرداخت</b>\n\n"
        f"💳 شماره کارت:\n"
        f"<code>{card_number}</code>\n\n"
        f"👤 به نام:\n"
        f"<b>{card_name}</b>\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "1️⃣ مبلغ را به شماره کارت بالا واریز کنید.\n\n"
        "2️⃣ سپس تصویر رسید پرداخت را برای ربات ارسال کنید.\n\n"
        f"🧾 شماره پرداخت شما: <code>#{payment_id}</code>\n\n"
        "بعد از بررسی رسید، اشتراک شما فعال خواهد شد."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ بازگشت به پلن‌ها",
                callback_data="subscription:back",
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )