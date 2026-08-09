import uuid

from src.generation.context_builder import build_context
from src.retrieval.models import RetrievedChunk


def test_build_context_numbers_chunks_with_section_and_page():
    chunks = [
        RetrievedChunk(document_id=uuid.uuid4(), chunk_index=0, content="alpha", section="Intro", page=1, score=0.1),
        RetrievedChunk(document_id=uuid.uuid4(), chunk_index=1, content="beta", section=None, page=None, score=0.2),
    ]

    context = build_context(chunks)

    assert context == "[1] (Intro, page 1): alpha\n\n[2]: beta"


def test_build_context_empty_list_returns_empty_string():
    assert build_context([]) == ""
