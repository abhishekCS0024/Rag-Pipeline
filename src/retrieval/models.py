# RetrievedChunk: a scored chunk returned from retrieval, carrying citation metadata.
import uuid
from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    document_id: uuid.UUID
    chunk_index: int
    content: str
    section: str | None
    page: int | None
    score: float  # cosine distance from the query embedding; lower is more similar
