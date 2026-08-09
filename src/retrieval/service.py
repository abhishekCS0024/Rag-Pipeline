# RetrievalService: top-level query pipeline entrypoint — dense + sparse retrieval, RRF fusion, optional rerank.
import uuid

from src.retrieval.dense import DenseRetriever
from src.retrieval.fusion import reciprocal_rank_fusion
from src.retrieval.models import RetrievedChunk
from src.retrieval.reranker import Reranker
from src.retrieval.sparse import SparseRetriever


class RetrievalService:
    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
        reranker: Reranker,
        dense_top_k: int,
        sparse_top_k: int,
        rrf_k: int,
        fusion_top_k: int,
        rerank_top_k: int,
    ):
        self._dense_retriever = dense_retriever
        self._sparse_retriever = sparse_retriever
        self._reranker = reranker
        self._dense_top_k = dense_top_k
        self._sparse_top_k = sparse_top_k
        self._rrf_k = rrf_k
        self._fusion_top_k = fusion_top_k
        self._rerank_top_k = rerank_top_k

    def retrieve(self, tenant_id: uuid.UUID, query: str) -> list[RetrievedChunk]:
        dense_results = self._dense_retriever.retrieve(tenant_id, query, self._dense_top_k)
        sparse_results = self._sparse_retriever.retrieve(tenant_id, query, self._sparse_top_k)
        fused = reciprocal_rank_fusion(dense_results, sparse_results, self._rrf_k, self._fusion_top_k)
        return self._reranker.rerank(query, fused, self._rerank_top_k)
