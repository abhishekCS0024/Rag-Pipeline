# pgvector-backed vector store: persists embedded chunks and serves tenant-filtered similarity search.
import uuid

from infrastructure.postgres.repositories.chunk_repository import SqlChunkRepository
from src.indexing.models import EmbeddedChunk
from src.retrieval.models import RetrievedChunk


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

    def delete_by_document(self, document_id: uuid.UUID) -> None:
        self._chunk_repository.delete_by_document(document_id)

    def search(self, tenant_id: uuid.UUID, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        rows = self._chunk_repository.similarity_search(tenant_id, query_embedding, top_k)
        return [
            RetrievedChunk(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                section=chunk.section,
                page=chunk.page,
                score=distance,
            )
            for chunk, distance in rows
        ]
