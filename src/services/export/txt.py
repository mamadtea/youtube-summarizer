from pathlib import Path
from datetime import datetime


def create_txt(
    summary: dict
) -> str:

    filename = (
        f"summary_"
        f"{datetime.now().timestamp()}.txt"
    )

    path = Path(
        "temp"
    )

    path.mkdir(
        exist_ok=True
    )

    file_path = path / filename


    content = f"""
YouTube Summary

====================

Title:
{summary.get("title", "")}


Summary:

{summary.get("summary", "")}


Key Points:

"""

    for point in summary.get(
        "key_points",
        []
    ):
        content += f"- {point}\n"


    file_path.write_text(
        content,
        encoding="utf-8"
    )


    return str(
        file_path
    )