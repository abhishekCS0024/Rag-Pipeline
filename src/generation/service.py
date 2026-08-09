# GenerationService: top-level generation orchestration (context build -> LLM call -> answer+citations).
from src.generation.context_builder import build_context
from src.generation.llm import LLMProvider
from src.generation.models import Citation, GeneratedAnswer
from src.generation.prompts import SYSTEM_PROMPT, build_user_prompt
from src.retrieval.models import RetrievedChunk


class GenerationService:
    def __init__(self, llm_provider: LLMProvider, max_context_chunks: int, return_citations: bool):
        self._llm_provider = llm_provider
        self._max_context_chunks = max_context_chunks
        self._return_citations = return_citations

    def generate(self, query: str, chunks: list[RetrievedChunk]) -> GeneratedAnswer:
        # ponytail: chunk-count cap only, not token-accurate against MAX_CONTEXT_TOKENS;
        # add real token counting if oversized chunks ever actually blow the context window.
        used_chunks = chunks[: self._max_context_chunks]
        context = build_context(used_chunks)
        user_prompt = build_user_prompt(query, context)
        answer = self._llm_provider.generate(SYSTEM_PROMPT, user_prompt)

        citations = [Citation.from_chunk(c) for c in used_chunks] if self._return_citations else []
        return GeneratedAnswer(answer=answer, citations=citations)
