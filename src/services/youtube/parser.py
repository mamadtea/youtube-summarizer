import re


class LinkParser:

    def extract_links(self, text: str):

        pattern = r"https?://\S+"

        return re.findall(
            pattern,
            text,
        )