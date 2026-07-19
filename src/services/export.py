import os
import logging
from typing import Dict, Any

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

logger = logging.getLogger("youtube_summarizer")

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


def _get_text(summary: Dict[str, Any]) -> str:
    """Extract and format text from summary dictionary."""
    text = summary.get("summary", "")
    
    key_points = summary.get("key_points", [])
    if key_points:
        text += "\n\n📌 Key Points:\n"
        for point in key_points:
            text += f"\n• {point}"
            
    terms = summary.get("terms", [])
    if terms:
        text += "\n\n📚 Terms:\n"
        for term in terms:
            text += f"\n• {term}"
            
    conclusion = summary.get("conclusion", "")
    if conclusion:
        text += f"\n\n⭐ Conclusion:\n{conclusion}"
            
    return text


def _reshape_rtl_text(text: str) -> str:
    """Reshape and reorder text for RTL rendering in PDF (Persian/Arabic support)."""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


def create_pdf(summary: Dict[str, Any]) -> str:
    """Generate a PDF file from the summary."""
    file_path = os.path.join(TEMP_DIR, f"summary_{id(summary)}.pdf")
    
    try:
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        # Starting position
        x = 20 * mm
        y = height - 20 * mm
        
        # Title
        c.setFont("Helvetica-Bold", 14)
        title = _reshape_rtl_text("YouTube Video Summary")
        c.drawCentredString(width / 2.0, y, title)
        y -= 15 * mm
        
        # Content
        c.setFont("Helvetica", 11)
        text_content = _get_text(summary)
        
        lines = text_content.split('\n')
        
        for line in lines:
            if y < 20 * mm:  # Check for page break
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


def create_txt(summary: Dict[str, Any]) -> str:
    """Generate a TXT file from the summary."""
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


def create_markdown(summary: Dict[str, Any]) -> str:
    """Generate a Markdown file from the summary."""
    file_path = os.path.join(TEMP_DIR, f"summary_{id(summary)}.md")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# 🎬 YouTube Video Summary\n\n")
            f.write(summary.get("summary", ""))
            
            key_points = summary.get("key_points", [])
            if key_points:
                f.write("\n\n## 📌 Key Points\n")
                for point in key_points:
                    f.write(f"- {point}\n")
                    
            terms = summary.get("terms", [])
            if terms:
                f.write("\n\n## 📚 Terms\n")
                for term in terms:
                    f.write(f"- {term}\n")
                    
            conclusion = summary.get("conclusion", "")
            if conclusion:
                f.write(f"\n\n## ⭐ Conclusion\n{conclusion}\n")
                    
        logger.info("Markdown export completed")
        return file_path
        
    except Exception as e:
        logger.error(f"Error creating Markdown: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise