# SQLAlchemy-based implementation of the DocumentRepository protocol (create/get/status updates).

import uuid

from sqlalchemy.orm import Session

from infrastructure.postgres.models.document import DocumentORM
from src.documents.models import Document
from src.shared.constants import DocumentStatus


def _to_domain(orm: DocumentORM) -> Document:
    return Document(
        id=orm.id,
        tenant_id=orm.tenant_id,
        filename=orm.filename,
        content_type=orm.content_type,
        storage_key=orm.storage_key,
        status=DocumentStatus(orm.status),
        checksum=orm.checksum,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


class SqlDocumentRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        tenant_id: uuid.UUID,
        filename: str,
        content_type: str,
        storage_key: str,
        checksum: str | None,
    ) -> Document:
        orm = DocumentORM(
            tenant_id=tenant_id,
            filename=filename,
            content_type=content_type,
            storage_key=storage_key,
            status=DocumentStatus.UPLOADED,
            checksum=checksum,
        )
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return _to_domain(orm)

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        orm = self._session.get(DocumentORM, document_id)
        return _to_domain(orm) if orm else None

    def update_status(self, document_id: uuid.UUID, status: DocumentStatus) -> None:
        orm = self._session.get(DocumentORM, document_id)
        if orm is None:
            return
        orm.status = status
        self._session.commit()

    def delete(self, document_id: uuid.UUID) -> None:
        orm = self._session.get(DocumentORM, document_id)
        if orm is None:
            return
        self._session.delete(orm)
        self._session.commit()
