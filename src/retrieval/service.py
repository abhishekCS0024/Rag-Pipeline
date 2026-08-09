# RetrievalService: top-level query pipeline entrypoint (dense-only for now; sparse+fusion+rerank layer in later).
import uuid

from src.retrieval.dense import DenseRetriever
from src.retrieval.models import RetrievedChunk


class RetrievalService:
    def __init__(self, dense_retriever: DenseRetriever, top_k: int):
        self._dense_retriever = dense_retriever
        self._top_k = top_k

    def retrieve(self, tenant_id: uuid.UUID, query: str) -> list[RetrievedChunk]:
        return self._dense_retriever.retrieve(tenant_id, query, self._top_k)
