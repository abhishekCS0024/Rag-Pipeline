import uuid

from src.generation.service import GenerationService
from src.retrieval.models import RetrievedChunk


class FakeLLMProvider:
    def __init__(self, reply: str = "the answer"):
        self.calls: list[tuple[str, str]] = []
        self._reply = reply

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return self._reply


def _chunk(index: int) -> RetrievedChunk:
    return RetrievedChunk(
        document_id=uuid.uuid4(), chunk_index=index, content=f"chunk {index}", section=None, page=None, score=0.1
    )


def test_generate_returns_answer_and_citations_for_used_chunks():
    llm_provider = FakeLLMProvider(reply="42")
    service = GenerationService(llm_provider, max_context_chunks=5, return_citations=True)
    chunks = [_chunk(0), _chunk(1)]

    result = service.generate("what is it?", chunks)

    assert result.answer == "42"
    assert [c.chunk_index for c in result.citations] == [0, 1]
    assert len(llm_provider.calls) == 1
    system_prompt, user_prompt = llm_provider.calls[0]
    assert "chunk 0" in user_prompt
    assert "chunk 1" in user_prompt
    assert "what is it?" in user_prompt


def test_generate_slices_chunks_to_max_context_chunks():
    llm_provider = FakeLLMProvider()
    service = GenerationService(llm_provider, max_context_chunks=1, return_citations=True)
    chunks = [_chunk(0), _chunk(1), _chunk(2)]

    result = service.generate("q", chunks)

    assert [c.chunk_index for c in result.citations] == [0]
    _, user_prompt = llm_provider.calls[0]
    assert "chunk 1" not in user_prompt
    assert "chunk 2" not in user_prompt


def test_generate_omits_citations_when_return_citations_false():
    llm_provider = FakeLLMProvider()
    service = GenerationService(llm_provider, max_context_chunks=5, return_citations=False)

    result = service.generate("q", [_chunk(0)])

    assert result.citations == []
