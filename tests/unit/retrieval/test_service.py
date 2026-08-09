import uuid

from src.retrieval.service import RetrievalService


class FakeDenseRetriever:
    def __init__(self, results):
        self.calls = []
        self._results = results

    def retrieve(self, tenant_id, query, top_k):
        self.calls.append((tenant_id, query, top_k))
        return self._results


def test_retrieve_delegates_to_dense_retriever_with_configured_top_k():
    tenant_id = uuid.uuid4()
    dense_retriever = FakeDenseRetriever(results=["chunk1", "chunk2"])
    service = RetrievalService(dense_retriever, top_k=7)

    results = service.retrieve(tenant_id, "what is rag?")

    assert dense_retriever.calls == [(tenant_id, "what is rag?", 7)]
    assert results == ["chunk1", "chunk2"]
