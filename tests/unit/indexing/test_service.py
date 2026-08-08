import uuid

from src.indexing.models import EmbeddedChunk
from src.indexing.service import IndexingService
from src.ingestion.models import Chunk
from src.shared.constants import DocumentStatus


class FakeEmbedder:
    def embed_chunks(self, chunks):
        return [EmbeddedChunk(chunk=c, embedding=[0.0]) for c in chunks]


class FakeStore:
    def __init__(self):
        self.calls = []

    def store(self, document_id, tenant_id, embedded_chunks):
        self.calls.append((document_id, tenant_id, embedded_chunks))


class FakeDocumentRepository:
    def __init__(self):
        self.statuses = []

    def create(self, **kwargs):
        raise NotImplementedError

    def get_by_id(self, document_id):
        raise NotImplementedError

    def update_status(self, document_id, status):
        self.statuses.append((document_id, status))


def test_index_embeds_stores_and_marks_completed():
    document_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    chunks = [Chunk(chunk_index=0, content="x", section=None, page=None)]

    store = FakeStore()
    document_repository = FakeDocumentRepository()
    service = IndexingService(FakeEmbedder(), store, document_repository)

    service.index(document_id, tenant_id, chunks)

    assert len(store.calls) == 1
    assert store.calls[0][0] == document_id
    assert store.calls[0][1] == tenant_id
    assert document_repository.statuses == [(document_id, DocumentStatus.COMPLETED)]
