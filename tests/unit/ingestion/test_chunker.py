from src.ingestion.chunker import chunk_document
from src.ingestion.models import ParsedDocument, ParsedSection


def test_chunk_document_splits_with_overlap():
    document = ParsedDocument(
        sections=[ParsedSection(text="a" * 25, section="Intro", page=1)]
    )

    chunks = chunk_document(document, chunk_size=10, chunk_overlap=4)

    assert [c.content for c in chunks] == ["a" * 10, "a" * 10, "a" * 10, "a" * 7]
    assert all(c.section == "Intro" and c.page == 1 for c in chunks)
    assert [c.chunk_index for c in chunks] == [0, 1, 2, 3]


def test_chunk_document_drops_blank_sections():
    document = ParsedDocument(
        sections=[
            ParsedSection(text="   ", section=None, page=None),
            ParsedSection(text="hello world", section="Body", page=2),
        ]
    )

    chunks = chunk_document(document, chunk_size=50, chunk_overlap=0)

    assert len(chunks) == 1
    assert chunks[0].content == "hello world"


def test_chunk_document_strips_metadata_when_disabled():
    document = ParsedDocument(
        sections=[ParsedSection(text="hello", section="Body", page=2)]
    )

    chunks = chunk_document(
        document,
        chunk_size=50,
        chunk_overlap=0,
        include_section_metadata=False,
        include_page_metadata=False,
    )

    assert chunks[0].section is None
    assert chunks[0].page is None
