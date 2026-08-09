import uuid
from dataclasses import dataclass

from infrastructure.vector.pgvector_store import PgVectorStore
from src.indexing.models import EmbeddedChunk
from src.ingestion.models import Chunk


@dataclass
class FakeChunkORM:
    document_id: uuid.UUID
    chunk_index: int
    content: str
    section: str | None
    page: int | None


class FakeChunkRepository:
    def __init__(self, search_results=None):
        self.calls: list[tuple] = []
        self.search_calls: list[tuple] = []
        self._search_results = search_results or []

    def bulk_insert(self, document_id, tenant_id, rows):
        self.calls.append((document_id, tenant_id, rows))

    def similarity_search(self, tenant_id, query_embedding, top_k):
        self.search_calls.append((tenant_id, query_embedding, top_k))
        return self._search_results


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


def test_search_maps_repository_rows_to_retrieved_chunks():
    document_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    repository = FakeChunkRepository(
        search_results=[
            (FakeChunkORM(document_id=document_id, chunk_index=0, content="a", section="S", page=1), 0.1),
            (FakeChunkORM(document_id=document_id, chunk_index=1, content="b", section=None, page=None), 0.5),
        ]
    )
    store = PgVectorStore(repository)

    results = store.search(tenant_id, [0.1, 0.2], top_k=5)

    assert repository.search_calls == [(tenant_id, [0.1, 0.2], 5)]
    assert [(r.content, r.score) for r in results] == [("a", 0.1), ("b", 0.5)]
    assert results[0].document_id == document_id
    assert results[0].section == "S"
    assert results[0].page == 1
