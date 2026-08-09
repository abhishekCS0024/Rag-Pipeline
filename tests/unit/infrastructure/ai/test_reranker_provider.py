import uuid

from infrastructure.ai.reranker_provider import CrossEncoderReranker
from src.retrieval.models import RetrievedChunk


class FakeModel:
    def __init__(self, scores):
        self.calls: list[list[tuple[str, str]]] = []
        self._scores = scores

    def predict(self, pairs):
        self.calls.append(pairs)
        return self._scores


def _provider(scores) -> tuple[CrossEncoderReranker, FakeModel]:
    # Bypass __init__ (which loads the real cross-encoder model) so unit
    # tests stay fast and don't require the model to be downloaded.
    provider = CrossEncoderReranker.__new__(CrossEncoderReranker)
    fake_model = FakeModel(scores)
    provider._model = fake_model
    return provider, fake_model


def _chunk(chunk_index, content):
    return RetrievedChunk(document_id=uuid.uuid4(), chunk_index=chunk_index, content=content, section=None, page=None, score=0.0)


def test_rerank_sorts_by_model_score_descending_and_slices_top_k():
    chunks = [_chunk(0, "low"), _chunk(1, "high"), _chunk(2, "mid")]
    provider, fake_model = _provider(scores=[0.1, 0.9, 0.5])

    result = provider.rerank("query", chunks, top_k=2)

    assert fake_model.calls == [[("query", "low"), ("query", "high"), ("query", "mid")]]
    assert [c.content for c in result] == ["high", "mid"]
    assert result[0].score == 0.9
    assert result[1].score == 0.5


def test_rerank_empty_list_makes_no_model_calls():
    provider, fake_model = _provider(scores=[])

    assert provider.rerank("query", [], top_k=5) == []
    assert fake_model.calls == []
