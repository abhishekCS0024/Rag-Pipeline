# Citation and GeneratedAnswer: domain models for the generation step's output.
import uuid
from dataclasses import dataclass, field

from src.retrieval.models import RetrievedChunk


@dataclass
class Citation:
    document_id: uuid.UUID
    chunk_index: int
    section: str | None
    page: int | None

    @classmethod
    def from_chunk(cls, chunk: RetrievedChunk) -> "Citation":
        return cls(
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            section=chunk.section,
            page=chunk.page,
        )


@dataclass
class GeneratedAnswer:
    answer: str
    citations: list[Citation] = field(default_factory=list)
