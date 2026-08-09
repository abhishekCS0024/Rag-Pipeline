import uuid

from src.retrieval.models import RetrievedChunk
from src.retrieval.sparse import SparseRetriever


class FakeSearcher:
    def __init__(self, results):
        self.calls = []
        self._results = results

    def search(self, tenant_id, query, top_k):
        self.calls.append((tenant_id, query, top_k))
        return self._results


def test_retrieve_searches_with_raw_query_tenant_and_top_k():
    tenant_id = uuid.uuid4()
    expected = [RetrievedChunk(document_id=uuid.uuid4(), chunk_index=0, content="x", section=None, page=None, score=0.5)]
    searcher = FakeSearcher(expected)
    retriever = SparseRetriever(searcher)

    results = retriever.retrieve(tenant_id, "what is rag?", top_k=3)

    assert searcher.calls == [(tenant_id, "what is rag?", 3)]
    assert results == expected
