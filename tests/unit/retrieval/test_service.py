import uuid

from src.retrieval.models import RetrievedChunk
from src.retrieval.service import RetrievalService


def _chunk(document_id, chunk_index, content, score=0.0):
    return RetrievedChunk(document_id=document_id, chunk_index=chunk_index, content=content, section=None, page=None, score=score)


class FakeDenseRetriever:
    def __init__(self, results):
        self.calls = []
        self._results = results

    def retrieve(self, tenant_id, query, top_k):
        self.calls.append((tenant_id, query, top_k))
        return self._results


class FakeSparseRetriever:
    def __init__(self, results):
        self.calls = []
        self._results = results

    def retrieve(self, tenant_id, query, top_k):
        self.calls.append((tenant_id, query, top_k))
        return self._results


class FakeReranker:
    def __init__(self, results):
        self.calls = []
        self._results = results

    def rerank(self, query, chunks, top_k):
        self.calls.append((query, chunks, top_k))
        return self._results


def test_retrieve_runs_dense_sparse_fusion_and_rerank_with_configured_top_ks():
    tenant_id = uuid.uuid4()
    doc_a = uuid.uuid4()
    dense_chunk = _chunk(doc_a, 0, "dense hit")
    sparse_chunk = _chunk(doc_a, 1, "sparse hit")
    reranked = [sparse_chunk, dense_chunk]

    dense_retriever = FakeDenseRetriever(results=[dense_chunk])
    sparse_retriever = FakeSparseRetriever(results=[sparse_chunk])
    reranker = FakeReranker(results=reranked)

    service = RetrievalService(
        dense_retriever,
        sparse_retriever,
        reranker,
        dense_top_k=20,
        sparse_top_k=15,
        rrf_k=60,
        fusion_top_k=30,
        rerank_top_k=5,
    )

    results = service.retrieve(tenant_id, "what is rag?")

    assert dense_retriever.calls == [(tenant_id, "what is rag?", 20)]
    assert sparse_retriever.calls == [(tenant_id, "what is rag?", 15)]

    assert len(reranker.calls) == 1
    rerank_query, fused_chunks, rerank_top_k = reranker.calls[0]
    assert rerank_query == "what is rag?"
    assert rerank_top_k == 5
    assert {c.content for c in fused_chunks} == {"dense hit", "sparse hit"}

    assert results == reranked
