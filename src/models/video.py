from dataclasses import dataclass, asdict
from typing import Optional



@dataclass
class Video:
    """
    Represents a YouTube video.
    """

    id: str
    url: str

    title: str = ""
    channel: str = ""
    duration: int = 0
    description: str = ""
    thumbnail: str = ""

    transcript: str = ""

    summary: Optional[dict] = None



    def to_dict(self) -> dict:
        """
        Convert Video object to JSON serializable dictionary.
        """

        return asdict(self)