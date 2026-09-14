import logging
import os

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from src.database import payments, subscriptions

load_dotenv()

logger = logging.getLogger("youtube_summarizer")


ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "").strip()


async def handle_receipt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Receive payment receipt from user and send it to admin.
    """

    if not update.message:
        return

    user = update.effective_user

    if not user:
        return

    user_id = user.id

    # ---------------------------------
    # Find latest pending payment
    # ---------------------------------

    payment = await payments.get_latest_pending_payment(
        user_id=user_id
    )

    if payment is None:
        await update.message.reply_text(
            "❌ پرداخت در انتظار رسیدی برای شما پیدا نشد.\n\n"
            "ابتدا از بخش /plans یک پلن انتخاب کنید."
        )
        return

    # ---------------------------------
    # Check photo
    # ---------------------------------

    if not update.message.photo:
        await update.message.reply_text(
            "❌ لطفاً تصویر رسید پرداخت را به صورت عکس ارسال کنید."
        )
        return

    # ---------------------------------
    # Select best resolution
    # ---------------------------------

    photo = update.message.photo[-1]

    file_id = photo.file_id

    # ---------------------------------
    # Save receipt
    # ---------------------------------

    saved = await payments.attach_receipt(
        payment_id=payment["id"],
        receipt_file_id=file_id,
    )

    if not saved:
        await update.message.reply_text(
            "❌ ذخیره رسید انجام نشد.\n"
            "لطفاً دوباره تلاش کنید."
        )
        return

    # ---------------------------------
    # Notify user
    # ---------------------------------

    await update.message.reply_text(
        "✅ <b>رسید شما دریافت شد.</b>\n\n"
        f"🧾 شماره پرداخت: <code>#{payment['id']}</code>\n"
        f"💳 پلن: <b>{payment['plan'].upper()}</b>\n"
        f"💰 مبلغ: <b>{payment['amount']:,} تومان</b>\n\n"
        "⏳ رسید شما برای بررسی ارسال شد.\n"
        "بعد از تأیید ادمین، اشتراک شما فعال خواهد شد.",
        parse_mode="HTML",
    )

    # ---------------------------------
    # Check admin configuration
    # ---------------------------------

    if not ADMIN_USER_ID:
        logger.error(
            "ADMIN_USER_ID is not configured."
        )

        await update.message.reply_text(
            "⚠️ رسید ثبت شد، اما ادمین هنوز تنظیم نشده است."
        )

        return

    try:
        admin_id = int(ADMIN_USER_ID)

    except ValueError:
        logger.error(
            "ADMIN_USER_ID must be an integer."
        )

        return

    # ---------------------------------
    # User information
    # ---------------------------------

    username = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    full_name = (
        user.full_name
        or "بدون نام"
    )

    # ---------------------------------
    # Admin message
    # ---------------------------------

    admin_text = (
        "🧾 <b>رسید پرداخت جدید</b>\n\n"
        f"🆔 Payment ID: <code>#{payment['id']}</code>\n"
        f"👤 User ID: <code>{user_id}</code>\n"
        f"👤 نام: <b>{full_name}</b>\n"
        f"🔗 Username: {username}\n\n"
        f"💳 پلن: <b>{payment['plan'].upper()}</b>\n"
        f"💰 مبلغ: <b>{payment['amount']:,} تومان</b>\n"
        f"📅 وضعیت: <b>PENDING</b>"
    )

    # ---------------------------------
    # Admin buttons
    # ---------------------------------

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ تأیید پرداخت",
                callback_data=(
                    f"payment:approve:{payment['id']}"
                ),
            ),
            InlineKeyboardButton(
                "❌ رد پرداخت",
                callback_data=(
                    f"payment:reject:{payment['id']}"
                ),
            ),
        ]
    ]

    # ---------------------------------
    # Send receipt to admin
    # ---------------------------------

    try:
        await context.bot.send_photo(
            chat_id=admin_id,
            photo=file_id,
            caption=admin_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            ),
        )

        logger.info(
            "Payment receipt sent to admin. "
            f"payment_id={payment['id']} "
            f"user_id={user_id}"
        )

    except Exception:
        logger.exception(
            "Failed to send payment receipt to admin."
        )


async def payment_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Handle admin approval/rejection of payments.
    """

    query = update.callback_query

    if not query:
        return

    await query.answer()

    # ---------------------------------
    # Check admin configuration
    # ---------------------------------

    if not ADMIN_USER_ID:
        await query.answer(
            "❌ ADMIN_USER_ID تنظیم نشده است.",
            show_alert=True,
        )
        return

    try:
        admin_id = int(ADMIN_USER_ID)

    except ValueError:
        await query.answer(
            "❌ ADMIN_USER_ID نامعتبر است.",
            show_alert=True,
        )
        return

    # ---------------------------------
    # Check Telegram user
    # ---------------------------------

    if not update.effective_user:
        return

    # ---------------------------------
    # Authorization
    # ---------------------------------

    if update.effective_user.id != admin_id:
        await query.answer(
            "⛔ شما دسترسی ادمین ندارید.",
            show_alert=True,
        )
        return

    # ---------------------------------
    # Parse callback data
    # ---------------------------------

    data = query.data or ""

    parts = data.split(":")

    if len(parts) != 3:
        await query.answer(
            "❌ اطلاعات پرداخت نامعتبر است.",
            show_alert=True,
        )
        return

    action = parts[1]

    try:
        payment_id = int(parts[2])

    except ValueError:
        await query.answer(
            "❌ شناسه پرداخت نامعتبر است.",
            show_alert=True,
        )
        return

    # ---------------------------------
    # Get payment
    # ---------------------------------

    payment = await payments.get_payment(
        payment_id
    )

    if payment is None:
        await query.answer(
            "❌ پرداخت پیدا نشد.",
            show_alert=True,
        )
        return

    # ---------------------------------
    # Approve payment
    # ---------------------------------

    if action == "approve":

        # Change PENDING -> PAID.
        #
        # This prevents the same payment
        # from being approved twice.

        updated = await payments.update_status(
            payment_id=payment_id,
            status="PAID",
        )

        if not updated:
            await query.answer(
                "⚠️ این پرداخت قبلاً بررسی شده است.",
                show_alert=True,
            )
            return

        # ---------------------------------
        # Activate subscription
        # ---------------------------------

        subscription = await subscriptions.activate(
            user_id=payment["user_id"],
            plan=payment["plan"],
        )

        # ---------------------------------
        # Update admin message
        # ---------------------------------

        await query.edit_message_caption(
            caption=(
                "✅ <b>پرداخت تأیید شد</b>\n\n"
                f"🧾 Payment ID: "
                f"<code>#{payment_id}</code>\n"
                f"👤 User ID: "
                f"<code>{payment['user_id']}</code>\n"
                f"💳 Plan: "
                f"<b>{payment['plan'].upper()}</b>\n"
                f"💰 Amount: "
                f"<b>{payment['amount']:,} تومان</b>\n\n"
                "🟢 اشتراک کاربر فعال شد.\n"
                f"📊 اعتبار: "
                f"<b>{subscription['credits_remaining']}</b>\n"
                "📅 اعتبار: <b>30 روز</b>"
            ),
            parse_mode="HTML",
        )

        # ---------------------------------
        # Notify user
        # ---------------------------------

        try:
            await context.bot.send_message(
                chat_id=payment["user_id"],
                text=(
                    "🎉 <b>پرداخت شما تأیید شد!</b>\n\n"
                    f"💳 پلن: "
                    f"<b>{payment['plan'].upper()}</b>\n"
                    f"📊 اعتبار: "
                    f"<b>{subscription['credits_remaining']} خلاصه</b>\n"
                    "📅 مدت اعتبار: <b>30 روز</b>\n\n"
                    "✅ اشتراک شما با موفقیت فعال شد.\n"
                    "اکنون می‌توانید از ربات استفاده کنید."
                ),
                parse_mode="HTML",
            )

        except Exception:
            logger.exception(
                "Failed to notify user after payment approval."
            )

        return

    # ---------------------------------
    # Reject payment
    # ---------------------------------

    if action == "reject":

        updated = await payments.update_status(
            payment_id=payment_id,
            status="REJECTED",
        )

        if not updated:
            await query.answer(
                "⚠️ این پرداخت قبلاً بررسی شده است.",
                show_alert=True,
            )
            return

        # ---------------------------------
        # Update admin message
        # ---------------------------------

        await query.edit_message_caption(
            caption=(
                "❌ <b>پرداخت رد شد</b>\n\n"
                f"🧾 Payment ID: "
                f"<code>#{payment_id}</code>\n"
                f"👤 User ID: "
                f"<code>{payment['user_id']}</code>\n"
                f"💳 Plan: "
                f"<b>{payment['plan'].upper()}</b>\n"
                f"💰 Amount: "
                f"<b>{payment['amount']:,} تومان</b>"
            ),
            parse_mode="HTML",
        )

        # ---------------------------------
        # Notify user
        # ---------------------------------

        try:
            await context.bot.send_message(
                chat_id=payment["user_id"],
                text=(
                    "❌ <b>پرداخت شما تأیید نشد.</b>\n\n"
                    f"🧾 شماره پرداخت: "
                    f"<code>#{payment_id}</code>\n\n"
                    "اگر فکر می‌کنید این اشتباه است، "
                    "لطفاً با پشتیبانی تماس بگیرید."
                ),
                parse_mode="HTML",
            )

        except Exception:
            logger.exception(
                "Failed to notify user after payment rejection."
            )

        return

    # ---------------------------------
    # Unknown action
    # ---------------------------------

    await query.answer(
        "❌ عملیات نامعتبر است.",
        show_alert=True,
    )