# ChunkStore Protocol - the vector-store persistence interface for storing embedded chunks.
import uuid
from typing import Protocol

from src.indexing.models import EmbeddedChunk


class ChunkStore(Protocol):
    def store(self, document_id: uuid.UUID, tenant_id: uuid.UUID, embedded_chunks: list[EmbeddedChunk]) -> None: ...

    def delete_by_document(self, document_id: uuid.UUID) -> None: ...
