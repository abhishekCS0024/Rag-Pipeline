from dataclasses import dataclass, field


@dataclass
class ParsedSection:
    text: str
    section: str | None
    page: int | None


@dataclass
class ParsedDocument:
    sections: list[ParsedSection]


@dataclass
class Chunk:
    chunk_index: int
    content: str
    section: str | None
    page: int | None
    chunk_metadata: dict = field(default_factory=dict)
