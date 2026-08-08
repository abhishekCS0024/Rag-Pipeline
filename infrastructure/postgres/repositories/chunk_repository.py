import uuid

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
