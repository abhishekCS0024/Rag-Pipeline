# Embedder service - pairs chunks with embeddings via the embedding provider.
from infrastructure.ai.embedding_provider import HuggingFaceEmbeddingProvider
from src.indexing.models import EmbeddedChunk
from src.ingestion.models import Chunk


class Embedder:
    def __init__(self, provider: HuggingFaceEmbeddingProvider):
        self._provider = provider

    def embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        if not chunks:
            return []
        vectors = self._provider.embed([chunk.content for chunk in chunks])
        return [EmbeddedChunk(chunk=chunk, embedding=vector) for chunk, vector in zip(chunks, vectors)]
