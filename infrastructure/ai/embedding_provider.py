from openai import OpenAI

from src.shared.config import Settings


class OpenAIEmbeddingProvider:
    def __init__(self, settings: Settings):
        self._client = OpenAI(api_key=settings.embedding_api_key)
        self._model = settings.embedding_model
        self._batch_size = settings.embedding_batch_size

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]
            response = self._client.embeddings.create(model=self._model, input=batch)
            vectors.extend(item.embedding for item in response.data)
        return vectors
