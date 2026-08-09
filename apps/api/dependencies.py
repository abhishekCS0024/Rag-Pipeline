# FastAPI dependency-injection factories (DB session, document service, etc) wired to concrete infra adapters.
from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session


from infrastructure.ai.embedding_provider import OpenAIEmbeddingProvider
from infrastructure.postgres.repositories.chunk_repository import SqlChunkRepository
from infrastructure.postgres.repositories.document_repository import SqlDocumentRepository
from infrastructure.postgres.session import SessionLocal
from infrastructure.storage import get_storage_backend
from infrastructure.vector.pgvector_store import PgVectorStore
from src.documents.service import DocumentService
from src.retrieval.dense import DenseRetriever
from src.retrieval.service import RetrievalService
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


def get_retrieval_service(session: Session = Depends(get_db_session)) -> RetrievalService:
    settings = get_settings()
    searcher = PgVectorStore(SqlChunkRepository(session))
    embedder = OpenAIEmbeddingProvider(settings)
    dense_retriever = DenseRetriever(embedder, searcher)
    return RetrievalService(dense_retriever, top_k=settings.dense_top_k)
