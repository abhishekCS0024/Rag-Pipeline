import uuid

from src.retrieval.models import RetrievedChunk
from src.retrieval.reranker import NoopReranker


def _chunk(chunk_index, content="x"):
    return RetrievedChunk(document_id=uuid.uuid4(), chunk_index=chunk_index, content=content, section=None, page=None, score=0.0)


def test_noop_reranker_slices_to_top_k_without_reordering():
    chunks = [_chunk(0), _chunk(1), _chunk(2)]
    reranker = NoopReranker()

    result = reranker.rerank("query", chunks, top_k=2)

    assert result == chunks[:2]


def test_noop_reranker_empty_list():
    reranker = NoopReranker()

    assert reranker.rerank("query", [], top_k=5) == []
