# LLMProvider Protocol: the generation-side interface infrastructure/ai/llm_provider.py implements.
from typing import Protocol


class LLMProvider(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str: ...
