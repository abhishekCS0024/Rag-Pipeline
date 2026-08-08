from infrastructure.ai.embedding_provider import OpenAIEmbeddingProvider
from src.shared.config import Settings


class FakeEmbeddingItem:
    def __init__(self, embedding: list[float]):
        self.embedding = embedding


class FakeEmbeddingResponse:
    def __init__(self, data: list[FakeEmbeddingItem]):
        self.data = data


class FakeEmbeddingsClient:
    def __init__(self):
        self.calls: list[list[str]] = []

    def create(self, model: str, input: list[str]) -> FakeEmbeddingResponse:
        self.calls.append(input)
        return FakeEmbeddingResponse([FakeEmbeddingItem([float(len(t))]) for t in input])


class FakeClient:
    def __init__(self):
        self.embeddings = FakeEmbeddingsClient()


def _settings(**overrides) -> Settings:
    defaults = dict(
        postgres_host="localhost",
        postgres_db="db",
        postgres_user="user",
        postgres_password="pw",
        embedding_api_key="test-key",
        embedding_batch_size=2,
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def _provider(settings: Settings | None = None) -> tuple[OpenAIEmbeddingProvider, FakeClient]:
    provider = OpenAIEmbeddingProvider(settings or _settings())
    fake_client = FakeClient()
    provider._client = fake_client
    return provider, fake_client


def test_embed_returns_one_vector_per_text_within_a_single_batch():
    provider, fake_client = _provider(_settings(embedding_batch_size=10))

    vectors = provider.embed(["ab", "abcd"])

    assert fake_client.embeddings.calls == [["ab", "abcd"]]
    assert vectors == [[2.0], [4.0]]


def test_embed_splits_texts_into_batches_of_configured_size():
    provider, fake_client = _provider(_settings(embedding_batch_size=2))

    vectors = provider.embed(["a", "bb", "ccc", "dddd", "e"])

    assert fake_client.embeddings.calls == [["a", "bb"], ["ccc", "dddd"], ["e"]]
    assert vectors == [[1.0], [2.0], [3.0], [4.0], [1.0]]


def test_embed_empty_list_makes_no_api_calls():
    provider, fake_client = _provider()

    assert provider.embed([]) == []
    assert fake_client.embeddings.calls == []
