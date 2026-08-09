# Reranker Protocol: the interface infrastructure/ai/reranker_provider.py implements.
from typing import Protocol

from src.retrieval.models import RetrievedChunk


class Reranker(Protocol):
    def rerank(self, query: str, chunks: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]: ...


class NoopReranker:
    """Used when reranking is disabled: just slices to top_k, no reordering."""

    def rerank(self, query: str, chunks: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
        return chunks[:top_k]
