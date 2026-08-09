# Reciprocal Rank Fusion: combines dense + sparse ranked lists into one hybrid ranking.
import uuid
from dataclasses import replace

from src.retrieval.models import RetrievedChunk


def reciprocal_rank_fusion(
    dense_results: list[RetrievedChunk],
    sparse_results: list[RetrievedChunk],
    k: int,
    top_k: int,
) -> list[RetrievedChunk]:
    scores: dict[tuple[uuid.UUID, int], float] = {}
    chunks: dict[tuple[uuid.UUID, int], RetrievedChunk] = {}

    for results in (dense_results, sparse_results):
        for rank, chunk in enumerate(results, start=1):
            key = (chunk.document_id, chunk.chunk_index)
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            chunks.setdefault(key, chunk)

    ranked_keys = sorted(scores, key=lambda key: scores[key], reverse=True)[:top_k]
    # RRF score is higher-is-better, unlike the dense stage's cosine distance.
    return [replace(chunks[key], score=scores[key]) for key in ranked_keys]
