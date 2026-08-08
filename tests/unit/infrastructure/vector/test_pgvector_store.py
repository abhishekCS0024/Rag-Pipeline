import uuid

from infrastructure.vector.pgvector_store import PgVectorStore
from src.indexing.models import EmbeddedChunk
from src.ingestion.models import Chunk


class FakeChunkRepository:
    def __init__(self):
        self.calls: list[tuple] = []

    def bulk_insert(self, document_id, tenant_id, rows):
        self.calls.append((document_id, tenant_id, rows))


def test_store_maps_embedded_chunks_to_repository_rows():
    document_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    embedded_chunks = [
        EmbeddedChunk(
            chunk=Chunk(chunk_index=0, content="hello", section="Intro", page=1, chunk_metadata={"k": "v"}),
            embedding=[0.1, 0.2],
        ),
        EmbeddedChunk(
            chunk=Chunk(chunk_index=1, content="world", section=None, page=None),
            embedding=[0.3, 0.4],
        ),
    ]
    repository = FakeChunkRepository()
    store = PgVectorStore(repository)

    store.store(document_id, tenant_id, embedded_chunks)

    assert len(repository.calls) == 1
    called_document_id, called_tenant_id, rows = repository.calls[0]
    assert called_document_id == document_id
    assert called_tenant_id == tenant_id
    assert rows == [
        {
            "chunk_index": 0,
            "content": "hello",
            "section": "Intro",
            "page": 1,
            "chunk_metadata": {"k": "v"},
            "embedding": [0.1, 0.2],
        },
        {
            "chunk_index": 1,
            "content": "world",
            "section": None,
            "page": None,
            "chunk_metadata": {},
            "embedding": [0.3, 0.4],
        },
    ]


def test_store_with_no_chunks_still_calls_repository_with_empty_rows():
    document_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    repository = FakeChunkRepository()
    store = PgVectorStore(repository)

    store.store(document_id, tenant_id, [])

    assert repository.calls == [(document_id, tenant_id, [])]
