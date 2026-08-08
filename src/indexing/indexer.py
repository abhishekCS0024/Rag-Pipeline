import uuid
from typing import Protocol

from src.indexing.models import EmbeddedChunk


class ChunkStore(Protocol):
    def store(self, document_id: uuid.UUID, tenant_id: uuid.UUID, embedded_chunks: list[EmbeddedChunk]) -> None: ...
