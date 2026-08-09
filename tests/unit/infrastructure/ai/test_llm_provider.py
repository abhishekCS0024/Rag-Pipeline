from infrastructure.ai.llm_provider import GroqLLMProvider


class FakeMessage:
    def __init__(self, content: str):
        self.content = content


class FakeChoice:
    def __init__(self, content: str):
        self.message = FakeMessage(content)


class FakeCompletion:
    def __init__(self, content: str):
        self.choices = [FakeChoice(content)]


class FakeCompletionsClient:
    def __init__(self, reply: str = "the answer"):
        self.calls: list[dict] = []
        self._reply = reply

    def create(self, **kwargs) -> FakeCompletion:
        self.calls.append(kwargs)
        return FakeCompletion(self._reply)


class FakeChatClient:
    def __init__(self, completions: FakeCompletionsClient):
        self.completions = completions


class FakeClient:
    def __init__(self, reply: str = "the answer"):
        self.completions = FakeCompletionsClient(reply)
        self.chat = FakeChatClient(self.completions)


def _provider(reply: str = "the answer", **overrides) -> tuple[GroqLLMProvider, FakeClient]:
    # Bypass __init__ (which constructs a real Groq client) so unit tests
    # don't need a real API key or network access.
    provider = GroqLLMProvider.__new__(GroqLLMProvider)
    fake_client = FakeClient(reply)
    provider._client = fake_client
    provider._model = overrides.get("model", "llama-3.1-8b-instant")
    provider._temperature = overrides.get("temperature", 0.1)
    provider._max_tokens = overrides.get("max_tokens", 2048)
    provider._timeout = overrides.get("timeout", 60)
    return provider, fake_client


def test_generate_sends_system_and_user_messages_and_returns_content():
    provider, fake_client = _provider(reply="hello there")

    answer = provider.generate("be nice", "say hi")

    assert answer == "hello there"
    assert fake_client.completions.calls == [
        {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "be nice"},
                {"role": "user", "content": "say hi"},
            ],
            "temperature": 0.1,
            "max_tokens": 2048,
            "timeout": 60,
        }
    ]


def test_generate_uses_configured_model_and_params():
    provider, fake_client = _provider(model="other-model", temperature=0.5, max_tokens=100, timeout=30)

    provider.generate("sys", "usr")

    call = fake_client.completions.calls[0]
    assert call["model"] == "other-model"
    assert call["temperature"] == 0.5
    assert call["max_tokens"] == 100
    assert call["timeout"] == 30
