# Groq-backed LLM provider for the generation/answer step of the query pipeline.
from groq import Groq

from src.shared.config import Settings


class GroqLLMProvider:
    def __init__(self, settings: Settings):
        self._client = Groq(api_key=settings.llm_api_key)
        self._model = settings.llm_model
        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens
        self._timeout = settings.llm_timeout_seconds

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            timeout=self._timeout,
        )
        return response.choices[0].message.content
