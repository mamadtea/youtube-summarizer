from pathlib import Path
from datetime import datetime



def create_markdown(
    summary: dict
) -> str:


    filename = (
        f"summary_"
        f"{datetime.now().timestamp()}.md"
    )


    path = Path(
        "temp"
    )


    path.mkdir(
        exist_ok=True
    )


    file_path = path / filename



    content = f"""
# {summary.get("title","")}


## Summary

{summary.get("summary","")}


## Key Points

"""


    for item in summary.get(
        "key_points",
        []
    ):

        content += (
            f"- {item}\n"
        )


    file_path.write_text(
        content,
        encoding="utf-8"
    )


    return str(
        file_path
    )