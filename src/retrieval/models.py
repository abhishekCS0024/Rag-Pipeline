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
    # Semantics depend on the stage that produced this chunk: dense = cosine
    # distance (lower is more similar), sparse = ts_rank (higher is better),
    # fused/reranked = stage-specific relevance score (higher is better).
    score: float
