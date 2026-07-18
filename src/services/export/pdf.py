from pathlib import Path
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet



def create_pdf(
    summary: dict
) -> str:


    filename = (
        f"summary_"
        f"{datetime.now().timestamp()}.pdf"
    )


    folder = Path(
        "temp"
    )


    folder.mkdir(
        exist_ok=True
    )


    file_path = folder / filename



    doc = SimpleDocTemplate(
        str(file_path)
    )


    styles = getSampleStyleSheet()


    story = []


    story.append(
        Paragraph(
            summary.get(
                "title",
                "YouTube Summary"
            ),
            styles["Title"]
        )
    )


    story.append(
        Spacer(
            1,
            12
        )
    )


    story.append(
        Paragraph(
            summary.get(
                "summary",
                ""
            ),
            styles["BodyText"]
        )
    )


    for item in summary.get(
        "key_points",
        []
    ):

        story.append(
            Paragraph(
                f"- {item}",
                styles["BodyText"]
            )
        )


    doc.build(
        story
    )


    return str(
        file_path
    )