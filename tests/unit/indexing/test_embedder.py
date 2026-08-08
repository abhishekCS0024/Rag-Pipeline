from src.indexing.embedder import Embedder
from src.ingestion.models import Chunk


class FakeProvider:
    def __init__(self):
        self.received: list[str] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.received = texts
        return [[float(len(t))] for t in texts]


def test_embed_chunks_pairs_vectors_with_chunks():
    chunks = [
        Chunk(chunk_index=0, content="ab", section=None, page=None),
        Chunk(chunk_index=1, content="abcd", section=None, page=None),
    ]
    provider = FakeProvider()
    embedder = Embedder(provider)

    result = embedder.embed_chunks(chunks)

    assert provider.received == ["ab", "abcd"]
    assert [ec.embedding for ec in result] == [[2.0], [4.0]]
    assert [ec.chunk for ec in result] == chunks


def test_embed_chunks_empty_list_short_circuits():
    provider = FakeProvider()
    embedder = Embedder(provider)

    assert embedder.embed_chunks([]) == []
