# SparseRetriever: keyword/full-text search over chunks, tenant-filtered.
import uuid
from typing import Protocol

from src.retrieval.models import RetrievedChunk


class KeywordSearcher(Protocol):
    def search(self, tenant_id: uuid.UUID, query: str, top_k: int) -> list[RetrievedChunk]: ...


class SparseRetriever:
    def __init__(self, searcher: KeywordSearcher):
        self._searcher = searcher

    def retrieve(self, tenant_id: uuid.UUID, query: str, top_k: int) -> list[RetrievedChunk]:
        return self._searcher.search(tenant_id, query, top_k)
