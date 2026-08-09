import uuid

from src.retrieval.dense import DenseRetriever
from src.retrieval.models import RetrievedChunk


class FakeEmbedder:
    def __init__(self):
        self.received: list[str] = []

    def embed(self, texts):
        self.received = texts
        return [[1.0, 2.0]]


class FakeSearcher:
    def __init__(self, results):
        self.calls = []
        self._results = results

    def search(self, tenant_id, query_embedding, top_k):
        self.calls.append((tenant_id, query_embedding, top_k))
        return self._results


def test_retrieve_embeds_query_and_searches_with_tenant_and_top_k():
    tenant_id = uuid.uuid4()
    expected = [RetrievedChunk(document_id=uuid.uuid4(), chunk_index=0, content="x", section=None, page=None, score=0.1)]
    embedder = FakeEmbedder()
    searcher = FakeSearcher(expected)
    retriever = DenseRetriever(embedder, searcher)

    results = retriever.retrieve(tenant_id, "what is rag?", top_k=3)

    assert embedder.received == ["what is rag?"]
    assert searcher.calls == [(tenant_id, [1.0, 2.0], 3)]
    assert results == expected
