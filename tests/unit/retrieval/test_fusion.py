import uuid

from src.retrieval.fusion import reciprocal_rank_fusion
from src.retrieval.models import RetrievedChunk


def _chunk(document_id, chunk_index, content="x"):
    return RetrievedChunk(document_id=document_id, chunk_index=chunk_index, content=content, section=None, page=None, score=0.0)


def test_fuse_combines_scores_for_chunk_appearing_in_both_lists():
    doc_a, doc_b = uuid.uuid4(), uuid.uuid4()
    shared = _chunk(doc_a, 0, "shared")
    dense_only = _chunk(doc_b, 0, "dense only")

    dense_results = [shared, dense_only]
    sparse_results = [shared]

    fused = reciprocal_rank_fusion(dense_results, sparse_results, k=60, top_k=10)

    assert [c.content for c in fused] == ["shared", "dense only"]
    shared_score = 1 / (60 + 1) + 1 / (60 + 1)
    dense_only_score = 1 / (60 + 2)
    assert fused[0].score == shared_score
    assert fused[1].score == dense_only_score


def test_fuse_respects_top_k_truncation():
    chunks = [_chunk(uuid.uuid4(), i) for i in range(5)]

    fused = reciprocal_rank_fusion(chunks, [], k=60, top_k=2)

    assert len(fused) == 2


def test_fuse_handles_empty_sparse_results():
    doc_id = uuid.uuid4()
    dense_results = [_chunk(doc_id, 0)]

    fused = reciprocal_rank_fusion(dense_results, [], k=60, top_k=10)

    assert len(fused) == 1
    assert fused[0].score == 1 / 61
