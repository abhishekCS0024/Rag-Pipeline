import uuid
from dataclasses import dataclass

from infrastructure.search.postgres_fts import PostgresFtsStore


@dataclass
class FakeChunkORM:
    document_id: uuid.UUID
    chunk_index: int
    content: str
    section: str | None
    page: int | None


class FakeChunkRepository:
    def __init__(self, results=None):
        self.calls = []
        self._results = results or []

    def keyword_search(self, tenant_id, query, top_k, language):
        self.calls.append((tenant_id, query, top_k, language))
        return self._results


def test_search_maps_repository_rows_to_retrieved_chunks():
    document_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    repository = FakeChunkRepository(
        results=[
            (FakeChunkORM(document_id=document_id, chunk_index=0, content="a", section="S", page=1), 0.9),
            (FakeChunkORM(document_id=document_id, chunk_index=1, content="b", section=None, page=None), 0.4),
        ]
    )
    store = PostgresFtsStore(repository, language="english")

    results = store.search(tenant_id, "hello world", top_k=5)

    assert repository.calls == [(tenant_id, "hello world", 5, "english")]
    assert [(r.content, r.score) for r in results] == [("a", 0.9), ("b", 0.4)]
    assert results[0].document_id == document_id
    assert results[0].section == "S"
    assert results[0].page == 1


def test_search_empty_results():
    store = PostgresFtsStore(FakeChunkRepository(), language="english")

    assert store.search(uuid.uuid4(), "query", top_k=5) == []
