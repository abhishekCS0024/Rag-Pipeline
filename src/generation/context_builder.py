# Formats retrieved chunks into a numbered context block for the LLM prompt; index maps 1:1 to citations.
from src.retrieval.models import RetrievedChunk


def build_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for i, chunk in enumerate(chunks, start=1):
        location = ", ".join(
            part
            for part in (chunk.section, f"page {chunk.page}" if chunk.page is not None else None)
            if part
        )
        header = f"[{i}] ({location})" if location else f"[{i}]"
        blocks.append(f"{header}: {chunk.content}")
    return "\n\n".join(blocks)
