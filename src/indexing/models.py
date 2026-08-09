# EmbeddedChunk and related indexing domain models.
from dataclasses import dataclass

from src.ingestion.models import Chunk


@dataclass
class EmbeddedChunk:
    chunk: Chunk
    embedding: list[float]
