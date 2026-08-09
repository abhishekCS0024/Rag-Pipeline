# Postgres full-text search adapter: keyword search over document_chunks.content, tenant-filtered.
import uuid

from infrastructure.postgres.repositories.chunk_repository import SqlChunkRepository
from src.retrieval.models import RetrievedChunk


class PostgresFtsStore:
    def __init__(self, chunk_repository: SqlChunkRepository, language: str):
        self._chunk_repository = chunk_repository
        self._language = language

    def search(self, tenant_id: uuid.UUID, query: str, top_k: int) -> list[RetrievedChunk]:
        rows = self._chunk_repository.keyword_search(tenant_id, query, top_k, self._language)
        return [
            RetrievedChunk(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                section=chunk.section,
                page=chunk.page,
                score=rank,
            )
            for chunk, rank in rows
        ]
