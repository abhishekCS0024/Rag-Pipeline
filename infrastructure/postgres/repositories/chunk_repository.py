# SQLAlchemy-based implementation of chunk persistence (bulk-inserts chunks+embeddings).

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.postgres.models.chunk import DocumentChunkORM


class SqlChunkRepository:
    def __init__(self, session: Session):
        self._session = session

    def bulk_insert(self, document_id: uuid.UUID, tenant_id: uuid.UUID, chunks: list[dict]) -> None:
        """chunks: list of {chunk_index, content, section, page, chunk_metadata, embedding}."""
        orms = [
            DocumentChunkORM(
                document_id=document_id,
                tenant_id=tenant_id,
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                section=chunk.get("section"),
                page=chunk.get("page"),
                chunk_metadata=chunk.get("chunk_metadata") or {},
                embedding=chunk["embedding"],
            )
            for chunk in chunks
        ]
        self._session.add_all(orms)
        self._session.commit()

    def delete_by_document(self, document_id: uuid.UUID) -> None:
        self._session.query(DocumentChunkORM).filter(DocumentChunkORM.document_id == document_id).delete()
        self._session.commit()

    def similarity_search(
        self, tenant_id: uuid.UUID, query_embedding: list[float], top_k: int
    ) -> list[tuple[DocumentChunkORM, float]]:
        """Returns (chunk, cosine_distance) pairs ordered nearest-first, filtered to tenant_id."""
        distance = DocumentChunkORM.embedding.cosine_distance(query_embedding)
        stmt = (
            select(DocumentChunkORM, distance.label("distance"))
            .where(DocumentChunkORM.tenant_id == tenant_id)
            .order_by(distance)
            .limit(top_k)
        )
        return [(row.DocumentChunkORM, row.distance) for row in self._session.execute(stmt)]
