# Local sentence-transformers embedding provider: batches chunk text into vectors for pgvector storage.

from src.shared.config import Settings


class HuggingFaceEmbeddingProvider:
    """Wraps sentence-transformers to embed text locally (no external API call).

    sentence-transformers (and its torch dependency) is imported lazily so this
    module doesn't require the heavy dependency chain unless a
    HuggingFaceEmbeddingProvider is actually instantiated, matching the
    lazy-import treatment already used for docling in
    infrastructure/parsing/docling_parser.py.
    """

    def __init__(self, settings: Settings):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(settings.embedding_model)
        self._batch_size = settings.embedding_batch_size

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._model.encode(texts, batch_size=self._batch_size).tolist()
