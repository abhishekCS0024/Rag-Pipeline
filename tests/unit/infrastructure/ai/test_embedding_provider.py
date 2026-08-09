from infrastructure.ai.embedding_provider import HuggingFaceEmbeddingProvider


class FakeVectors(list):
    def tolist(self):
        return list(self)


class FakeModel:
    def __init__(self):
        self.calls: list[tuple[list[str], int]] = []

    def encode(self, texts: list[str], batch_size: int) -> FakeVectors:
        self.calls.append((texts, batch_size))
        return FakeVectors([float(len(t))] for t in texts)


def _provider(batch_size: int = 32) -> tuple[HuggingFaceEmbeddingProvider, FakeModel]:
    # Bypass __init__ (which loads the real sentence-transformers model) so
    # unit tests stay fast and don't require the model to be downloaded.
    provider = HuggingFaceEmbeddingProvider.__new__(HuggingFaceEmbeddingProvider)
    fake_model = FakeModel()
    provider._model = fake_model
    provider._batch_size = batch_size
    return provider, fake_model


def test_embed_passes_texts_and_batch_size_to_model():
    provider, fake_model = _provider(batch_size=10)

    vectors = provider.embed(["ab", "abcd"])

    assert fake_model.calls == [(["ab", "abcd"], 10)]
    assert vectors == [[2.0], [4.0]]


def test_embed_empty_list_makes_no_model_calls():
    provider, fake_model = _provider()

    assert provider.embed([]) == []
    assert fake_model.calls == []
