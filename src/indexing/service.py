# IndexingService - orchestrates embedding chunks and storing them into the vector store, updating document status.
import uuid

from src.documents.repository import DocumentRepository
from src.indexing.embedder import Embedder
from src.indexing.indexer import ChunkStore
from src.ingestion.models import Chunk
from src.shared.constants import DocumentStatus


class IndexingService:
    def __init__(self, embedder: Embedder, store: ChunkStore, document_repository: DocumentRepository):
        self._embedder = embedder
        self._store = store
        self._document_repository = document_repository

    def index(self, document_id: uuid.UUID, tenant_id: uuid.UUID, chunks: list[Chunk]) -> None:
        embedded_chunks = self._embedder.embed_chunks(chunks)
        self._store.store(document_id, tenant_id, embedded_chunks)
        self._document_repository.update_status(document_id, DocumentStatus.COMPLETED)
