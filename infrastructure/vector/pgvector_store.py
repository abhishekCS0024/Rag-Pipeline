import uuid

from infrastructure.postgres.repositories.chunk_repository import SqlChunkRepository
from src.indexing.models import EmbeddedChunk


class PgVectorStore:
    def __init__(self, chunk_repository: SqlChunkRepository):
        self._chunk_repository = chunk_repository

    def store(self, document_id: uuid.UUID, tenant_id: uuid.UUID, embedded_chunks: list[EmbeddedChunk]) -> None:
        rows = [
            {
                "chunk_index": ec.chunk.chunk_index,
                "content": ec.chunk.content,
                "section": ec.chunk.section,
                "page": ec.chunk.page,
                "chunk_metadata": ec.chunk.chunk_metadata,
                "embedding": ec.embedding,
            }
            for ec in embedded_chunks
        ]
        self._chunk_repository.bulk_insert(document_id, tenant_id, rows)
