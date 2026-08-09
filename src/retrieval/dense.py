# DenseRetriever: embeds the query text and searches the vector store for the nearest chunks, tenant-filtered.
import uuid
from typing import Protocol

from src.retrieval.models import RetrievedChunk


class VectorSearcher(Protocol):
    def search(self, tenant_id: uuid.UUID, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]: ...


class QueryEmbedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class DenseRetriever:
    def __init__(self, embedder: QueryEmbedder, searcher: VectorSearcher):
        self._embedder = embedder
        self._searcher = searcher

    def retrieve(self, tenant_id: uuid.UUID, query: str, top_k: int) -> list[RetrievedChunk]:
        query_embedding = self._embedder.embed([query])[0]
        return self._searcher.search(tenant_id, query_embedding, top_k)
