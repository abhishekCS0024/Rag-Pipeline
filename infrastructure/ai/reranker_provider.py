# Local cross-encoder reranker: scores (query, chunk) pairs and reorders by relevance.
from dataclasses import replace

from src.retrieval.models import RetrievedChunk
from src.shared.config import Settings


class CrossEncoderReranker:
    """Wraps a sentence-transformers CrossEncoder to rerank retrieved chunks.

    sentence-transformers is imported lazily so this module doesn't require
    the heavy dependency chain unless a CrossEncoderReranker is actually
    instantiated, matching the treatment already used for
    HuggingFaceEmbeddingProvider and DoclingParser.
    """

    def __init__(self, settings: Settings):
        from sentence_transformers import CrossEncoder

        self._model = CrossEncoder(settings.reranker_model)

    def rerank(self, query: str, chunks: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
        if not chunks:
            return []
        pairs = [(query, chunk.content) for chunk in chunks]
        scores = self._model.predict(pairs)
        ranked = sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)
        return [replace(chunk, score=float(score)) for chunk, score in ranked[:top_k]]
