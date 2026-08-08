from src.ingestion.models import Chunk, ParsedDocument


def chunk_document(
    document: ParsedDocument,
    chunk_size: int,
    chunk_overlap: int,
    include_section_metadata: bool = True,
    include_page_metadata: bool = True,
) -> list[Chunk]:
    """Splits each parsed section into overlapping character windows of
    ~chunk_size, preserving the section/page it came from so citations stay
    traceable back to the source.
    """
    chunks: list[Chunk] = []
    step = max(chunk_size - chunk_overlap, 1)

    for parsed_section in document.sections:
        text = parsed_section.text
        if not text:
            continue

        for start in range(0, len(text), step):
            window = text[start : start + chunk_size]
            if not window.strip():
                continue

            chunks.append(
                Chunk(
                    chunk_index=len(chunks),
                    content=window,
                    section=parsed_section.section if include_section_metadata else None,
                    page=parsed_section.page if include_page_metadata else None,
                )
            )

            if start + chunk_size >= len(text):
                break

    return chunks
