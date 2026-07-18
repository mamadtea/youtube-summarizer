from src.models.video import Video
def format_summary(
    video: Video,
    summary: dict
) -> str:

    if summary is None:
        summary = {}

    overview = summary.get(
        "overview",
        "خلاصه‌ای تولید نشد."
    )

    key_points = summary.get(
        "key_points",
        []
    )

    important_terms = summary.get(
        "important_terms",
        []
    )

    tools = summary.get(
        "tools",
        []
    )

    resources = summary.get(
        "resources",
        []
    )

    takeaway = summary.get(
        "final_takeaway",
        ""
    )

    text = f"""🎬 {video.title}

📺 {video.channel}

⏱ {video.duration}

━━━━━━━━━━━━━━━━━━

🧠 خلاصه

{overview}
"""

    if key_points:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "📌 نکات مهم\n\n"

        for item in key_points:

            text += f"• {item}\n"

    if important_terms:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "📚 اصطلاحات مهم\n\n"

        for item in important_terms:

            text += f"• {item}\n"

    if tools:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "🛠 ابزارها\n\n"

        for item in tools:

            text += f"• {item}\n"

    if resources:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "🔗 منابع\n\n"

        for item in resources:

            text += f"• {item}\n"

    if takeaway:

        text += "\n━━━━━━━━━━━━━━━━━━\n"

        text += "🎯 نتیجه نهایی\n\n"

        text += takeaway

    text += "\n\n━━━━━━━━━━━━━━━━━━"

    text += "\n🤖 Powered by AI"

    return text