# Handles document.uploaded events: downloads from S3, parses with Docling, chunks, embeds, and stores in pgvector, driving UPLOADED -> PROCESSING -> COMPLETED|FAILED.
import uuid

from infrastructure.ai.embedding_provider import HuggingFaceEmbeddingProvider
from infrastructure.postgres.repositories.chunk_repository import SqlChunkRepository
from infrastructure.postgres.repositories.document_repository import SqlDocumentRepository
from infrastructure.postgres.session import SessionLocal
from infrastructure.storage import get_storage_backend
from infrastructure.vector.pgvector_store import PgVectorStore
from src.indexing.embedder import Embedder
from src.indexing.service import IndexingService
from src.ingestion.service import IngestionService
from src.shared.config import get_settings
from src.shared.constants import DocumentStatus
from src.shared.exceptions import DocumentNotFoundError
from src.shared.logging import get_logger

logger = get_logger(__name__)


def handle_document_uploaded(payload: dict) -> None:
    document_id = uuid.UUID(payload["document_id"])
    tenant_id = uuid.UUID(payload["tenant_id"])

    session = SessionLocal()
    try:
        document_repository = SqlDocumentRepository(session)
        document = document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"document {document_id} not found")

        document_repository.update_status(document_id, DocumentStatus.PROCESSING)

        try:
            settings = get_settings()
            storage = get_storage_backend(settings)
            ingestion_service = IngestionService(storage)
            chunks = ingestion_service.process(document)

            embedder = Embedder(HuggingFaceEmbeddingProvider(settings))
            store = PgVectorStore(SqlChunkRepository(session))
            indexing_service = IndexingService(embedder, store, document_repository)
            indexing_service.index(document_id, tenant_id, chunks)
        except Exception:
            logger.exception("failed to process document %s", document_id)
            document_repository.update_status(document_id, DocumentStatus.FAILED)
            raise
    finally:
        session.close()
