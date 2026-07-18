from dataclasses import dataclass, field


@dataclass
class Summary:
    """
    Structured AI summary of a YouTube video.
    """

    summary: str

    key_points: list[str] = field(default_factory=list)

    links: list[str] = field(default_factory=list)

    tools: list[str] = field(default_factory=list)

    books: list[str] = field(default_factory=list)

    channels: list[str] = field(default_factory=list)

    resources: list[str] = field(default_factory=list)

    action_items: list[str] = field(default_factory=list)

    quotes: list[str] = field(default_factory=list)

    tags: list[str] = field(default_factory=list)

    timeline: list[str] = field(default_factory=list)

    category: str = ""

    difficulty: str = ""

    takeaway: str = ""