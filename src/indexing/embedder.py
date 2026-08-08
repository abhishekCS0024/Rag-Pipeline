from infrastructure.ai.embedding_provider import OpenAIEmbeddingProvider
from src.indexing.models import EmbeddedChunk
from src.ingestion.models import Chunk


class Embedder:
    def __init__(self, provider: OpenAIEmbeddingProvider):
        self._provider = provider

    def embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        if not chunks:
            return []
        vectors = self._provider.embed([chunk.content for chunk in chunks])
        return [EmbeddedChunk(chunk=chunk, embedding=vector) for chunk, vector in zip(chunks, vectors)]
