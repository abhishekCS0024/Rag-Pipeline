"""Requires `make up` + `make migrate` (real Postgres with pgvector reachable via .env)."""
import uuid

import pytest
from sqlalchemy import select

from infrastructure.postgres.models.chunk import DocumentChunkORM
from infrastructure.postgres.repositories.chunk_repository import SqlChunkRepository
from infrastructure.postgres.repositories.document_repository import SqlDocumentRepository
from infrastructure.postgres.session import SessionLocal
from src.shared.config import get_settings


@pytest.fixture
def session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _embedding(seed: float) -> list[float]:
    dim = get_settings().embedding_dimension
    return [seed] * dim


def test_bulk_insert_and_similarity_order(session):
    tenant_id = uuid.uuid4()
    document = SqlDocumentRepository(session).create(
        tenant_id=tenant_id,
        filename="doc.pdf",
        content_type="application/pdf",
        storage_key=f"tenants/{tenant_id}/documents/{uuid.uuid4()}/doc.pdf",
        checksum=None,
    )

    chunk_repository = SqlChunkRepository(session)
    chunk_repository.bulk_insert(
        document.id,
        tenant_id,
        [
            {"chunk_index": 0, "content": "close", "section": None, "page": None, "embedding": _embedding(1.0)},
            {"chunk_index": 1, "content": "far", "section": None, "page": None, "embedding": _embedding(100.0)},
        ],
    )

    query_vector = _embedding(1.0)
    rows = session.scalars(
        select(DocumentChunkORM)
        .where(DocumentChunkORM.tenant_id == tenant_id)
        .order_by(DocumentChunkORM.embedding.cosine_distance(query_vector))
    ).all()

    assert [r.content for r in rows] == ["close", "far"]


def test_delete_by_document_removes_only_that_documents_chunks(session):
    tenant_id = uuid.uuid4()
    document_repository = SqlDocumentRepository(session)
    keep = document_repository.create(
        tenant_id=tenant_id,
        filename="keep.pdf",
        content_type="application/pdf",
        storage_key=f"tenants/{tenant_id}/documents/{uuid.uuid4()}/keep.pdf",
        checksum=None,
    )
    remove = document_repository.create(
        tenant_id=tenant_id,
        filename="remove.pdf",
        content_type="application/pdf",
        storage_key=f"tenants/{tenant_id}/documents/{uuid.uuid4()}/remove.pdf",
        checksum=None,
    )

    chunk_repository = SqlChunkRepository(session)
    chunk_repository.bulk_insert(
        keep.id, tenant_id, [{"chunk_index": 0, "content": "a", "section": None, "page": None, "embedding": _embedding(1.0)}]
    )
    chunk_repository.bulk_insert(
        remove.id, tenant_id, [{"chunk_index": 0, "content": "b", "section": None, "page": None, "embedding": _embedding(2.0)}]
    )

    chunk_repository.delete_by_document(remove.id)

    remaining = session.scalars(select(DocumentChunkORM).where(DocumentChunkORM.tenant_id == tenant_id)).all()
    assert [r.document_id for r in remaining] == [keep.id]
