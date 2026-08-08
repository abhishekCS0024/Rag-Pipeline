"""Requires `make up` + `make migrate` (real Postgres reachable via .env)."""
import uuid

import pytest

from infrastructure.postgres.session import SessionLocal
from infrastructure.postgres.repositories.document_repository import SqlDocumentRepository
from src.shared.constants import DocumentStatus


@pytest.fixture
def session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_and_fetch_document(session):
    repository = SqlDocumentRepository(session)
    tenant_id = uuid.uuid4()

    created = repository.create(
        tenant_id=tenant_id,
        filename="trd.pdf",
        content_type="application/pdf",
        storage_key=f"tenants/{tenant_id}/documents/{uuid.uuid4()}/trd.pdf",
        checksum=None,
    )

    assert created.status == DocumentStatus.UPLOADED

    fetched = repository.get_by_id(created.id)
    assert fetched is not None
    assert fetched.filename == "trd.pdf"

    repository.update_status(created.id, DocumentStatus.COMPLETED)
    assert repository.get_by_id(created.id).status == DocumentStatus.COMPLETED
