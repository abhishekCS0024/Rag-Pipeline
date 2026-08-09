# FastAPI dependency-injection factories (DB session, document service, etc) wired to concrete infra adapters.
from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session


from infrastructure.ai.embedding_provider import HuggingFaceEmbeddingProvider
from infrastructure.ai.llm_provider import GroqLLMProvider
from infrastructure.ai.reranker_provider import CrossEncoderReranker
from infrastructure.postgres.repositories.chunk_repository import SqlChunkRepository
from infrastructure.postgres.repositories.document_repository import SqlDocumentRepository
from infrastructure.postgres.session import SessionLocal
from infrastructure.search.postgres_fts import PostgresFtsStore
from infrastructure.storage import get_storage_backend
from infrastructure.vector.pgvector_store import PgVectorStore
from src.documents.service import DocumentService
from src.generation.service import GenerationService
from src.retrieval.dense import DenseRetriever
from src.retrieval.reranker import NoopReranker
from src.retrieval.service import RetrievalService
from src.retrieval.sparse import SparseRetriever
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
    chunk_repository = SqlChunkRepository(session)

    embedder = HuggingFaceEmbeddingProvider(settings)
    dense_retriever = DenseRetriever(embedder, PgVectorStore(chunk_repository))

    fts_store = PostgresFtsStore(chunk_repository, settings.fts_language)
    sparse_retriever = SparseRetriever(fts_store)

    reranker = CrossEncoderReranker(settings) if settings.reranking_enabled else NoopReranker()

    return RetrievalService(
        dense_retriever,
        sparse_retriever,
        reranker,
        dense_top_k=settings.dense_top_k,
        sparse_top_k=settings.sparse_top_k,
        rrf_k=settings.rrf_k,
        fusion_top_k=settings.fusion_top_k,
        rerank_top_k=settings.rerank_top_k,
    )


def get_generation_service() -> GenerationService:
    settings = get_settings()
    llm_provider = GroqLLMProvider(settings)
    return GenerationService(
        llm_provider,
        max_context_chunks=settings.max_context_chunks,
        return_citations=settings.return_citations,
    )
