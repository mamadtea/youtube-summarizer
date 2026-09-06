from typing import Dict, Any

def format_summary(summary: Dict[str, Any]) -> str:
    if isinstance(summary, str):
        return f"🎬 خلاصه\n\n━━━━━━━━━━━━━━\n\n{summary}"

    text = "🎬 خلاصه\n\n━━━━━━━━━━━━━━\n\n"
    text += summary.get("summary", "")
    
    key_points = summary.get("key_points", [])
    if key_points:
        text += "\n\n📌 نکات کلیدی:\n"
        for point in key_points:
            text += f"\n• {point}"

    terms = summary.get("terms", [])
    if terms:
        text += "\n\n📚 اصطلاحات مهم:\n"
        for term in terms:
            text += f"\n• {term}"

    conclusion = summary.get("conclusion", "")
    if conclusion:
        text += f"\n\n⭐ نتیجه نهایی:\n{conclusion}"
        
    return text