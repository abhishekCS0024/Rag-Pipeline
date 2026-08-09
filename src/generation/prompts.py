# Prompt templates for the generation step: system instructions + user prompt assembly.

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions using only the provided context. "
    "Cite the sources you used with bracketed numbers like [1] or [2], matching the "
    "source numbers in the context. If the context doesn't contain the answer, say so "
    "instead of guessing."
)


def build_user_prompt(query: str, context: str) -> str:
    return f"Context:\n{context}\n\nQuestion: {query}"
