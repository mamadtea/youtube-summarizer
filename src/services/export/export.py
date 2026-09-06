import os
import logging
import typing

# ایمپورت امن کتابخانه‌ها (تا در صورت نصب نبودن، ربات کرش نکند)
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RTL = True
except ImportError:
    HAS_RTL = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

logger = logging.getLogger("youtube_summarizer")

TEMP_DIR = "temp"

# ساخت پوشه موقت
try:
    os.makedirs(TEMP_DIR, exist_ok=True)
except OSError as e:
    logger.error(f"Could not create temp directory: {e}")


def _get_text(summary: typing.Any) -> str:
    """تبدیل دیکشنری خلاصه به متن قابل ذخیره"""
    if isinstance(summary, str):
        return summary
        
    if not isinstance(summary, dict):
        return str(summary)

    text = summary.get("summary", "")
    
    key_points = summary.get("key_points", [])
    if key_points and isinstance(key_points, list):
        text += "\n\n📌 Key Points:\n" + "\n".join([f"• {p}" for p in key_points if p])
        
    terms = summary.get("terms", [])
    if terms and isinstance(terms, list):
        text += "\n\n📚 Terms:\n" + "\n".join([f"• {t}" for t in terms if t])
        
    conclusion = summary.get("conclusion", "")
    if conclusion:
        text += f"\n\n⭐ Conclusion:\n{conclusion}"
        
    return text


def _reshape_rtl_text(text: str) -> str:
    """اصلاح متن فارسی برای PDF"""
    if HAS_RTL:
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception:
            return text
    return text


def create_pdf(summary: typing.Any) -> typing.Optional[str]:
    """تولید فایل PDF"""
    if not HAS_PDF:
        raise Exception("ReportLab is not installed. Cannot generate PDF.")

    file_path = os.path.join(TEMP_DIR, f"summary_{id(summary)}.pdf")
    
    try:
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        x, y = 20 * mm, height - 20 * mm
        
        # تیتر
        c.setFont("Helvetica-Bold", 14)
        title = _reshape_rtl_text("YouTube Video Summary")
        c.drawCentredString(width / 2.0, y, title)
        y -= 15 * mm
        
        # محتوا
        c.setFont("Helvetica", 11)
        text_content = _get_text(summary)
        
        lines = text_content.split('\n')
        
        for line in lines:
            if y < 20 * mm:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 20 * mm
                
            display_line = _reshape_rtl_text(line) if line.strip() else ""
            c.drawString(x, y, display_line)
            y -= 7 * mm
            
        c.save()
        logger.info("PDF export completed")
        return file_path
        
    except Exception as e:
        logger.error(f"Error creating PDF: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise


def create_txt(summary: typing.Any) -> typing.Optional[str]:
    """تولید فایل TXT"""
    file_path = os.path.join(TEMP_DIR, f"summary_{id(summary)}.txt")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(_get_text(summary))
        logger.info("TXT export completed")
        return file_path
        
    except Exception as e:
        logger.error(f"Error creating TXT: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise


def create_markdown(summary: typing.Any) -> typing.Optional[str]:
    """تولید فایل Markdown"""
    file_path = os.path.join(TEMP_DIR, f"summary_{id(summary)}.md")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# 🎬 YouTube Video Summary\n\n")
            
            if isinstance(summary, dict):
                f.write(summary.get("summary", ""))
                
                key_points = summary.get("key_points", [])
                if key_points and isinstance(key_points, list):
                    f.write("\n\n## 📌 Key Points\n")
                    for point in key_points:
                        f.write(f"- {point}\n")
                        
                terms = summary.get("terms", [])
                if terms and isinstance(terms, list):
                    f.write("\n\n## 📚 Terms\n")
                    for term in terms:
                        f.write(f"- {term}\n")
                        
                conclusion = summary.get("conclusion", "")
                if conclusion:
                    f.write(f"\n\n## ⭐ Conclusion\n{conclusion}\n")
            else:
                f.write(str(summary))
                
        logger.info("Markdown export completed")
        return file_path
        
    except Exception as e:
        logger.error(f"Error creating Markdown: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise