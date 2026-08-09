# FastAPI dependency-injection factories (DB session, document service, etc) wired to concrete infra adapters.
from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session


from infrastructure.postgres.repositories.document_repository import SqlDocumentRepository
from infrastructure.postgres.session import SessionLocal
from infrastructure.storage import get_storage_backend
from src.documents.service import DocumentService
from src.shared.config import get_settings


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_document_service(session: Session = Depends(get_db_session)) -> DocumentService:
    repository = SqlDocumentRepository(session)
    storage = get_storage_backend(get_settings())
    return DocumentService(repository, storage)
