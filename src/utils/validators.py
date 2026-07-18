from urllib.parse import urlparse


YOUTUBE_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "m.youtube.com",
}


def is_youtube_url(url: str) -> bool:

    parsed = urlparse(url)

    return parsed.netloc in YOUTUBE_DOMAINS