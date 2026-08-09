# Handles document.delete events: removes the stored file and the document row (chunks cascade via FK).
import uuid

from infrastructure.postgres.repositories.document_repository import SqlDocumentRepository
from infrastructure.postgres.session import SessionLocal
from infrastructure.storage import get_storage_backend
from src.shared.config import get_settings
from src.shared.logging import get_logger

logger = get_logger(__name__)


def handle_document_delete(payload: dict) -> None:
    document_id = uuid.UUID(payload["document_id"])

    session = SessionLocal()
    try:
        document_repository = SqlDocumentRepository(session)
        document = document_repository.get_by_id(document_id)
        if document is None:
            logger.info("document %s already deleted, skipping", document_id)
            return

        settings = get_settings()
        storage = get_storage_backend(settings)
        storage.delete(document.storage_key)

        document_repository.delete(document_id)
    finally:
        session.close()
