# src/documents/repository.py
#         ↓
# What operations does the application need?

# infrastructure/postgres/repositories/document_repository.py
#         ↓
# How are those operations implemented using PostgreSQL?


# separating business logic from database logic
# Think of a repository as an abstraction over persistence.
# DocumentService save or retrieve a document without knowing that PostgreSQL and SQLAlchemy are being used


import uuid
from typing import Protocol

from src.documents.models import Document
from src.shared.constants import DocumentStatus


class DocumentRepository(Protocol):
    def create(
        self,
        tenant_id: uuid.UUID,
        filename: str,
        content_type: str,
        storage_key: str,
        checksum: str | None,
    ) -> Document: ...

    def get_by_id(self, document_id: uuid.UUID) -> Document | None: ...

    def update_status(self, document_id: uuid.UUID, status: DocumentStatus) -> None: ...
