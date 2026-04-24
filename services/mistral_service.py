from types import SimpleNamespace

import httpx

from config import MISTRAL_API_KEY


class _MistralHTTPClient:
    """Fallback client when the mistralai SDK is unavailable."""

    BASE_URL = "https://api.mistral.ai/v1"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("MISTRAL_API_KEY is missing in environment variables.")

        self._api_key = api_key
        self.embeddings = _EmbeddingsAPI(self)
        self.chat = _ChatAPI(self)

    def _post(self, endpoint: str, payload: dict):
        response = httpx.post(
            f"{self.BASE_URL}{endpoint}",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()


class _EmbeddingsAPI:
    def __init__(self, parent: _MistralHTTPClient):
        self._parent = parent

    def create(self, model: str, inputs):
        data = self._parent._post(
            "/embeddings",
            {"model": model, "input": inputs},
        )
        wrapped = [SimpleNamespace(**item) for item in data.get("data", [])]
        return SimpleNamespace(data=wrapped)


class _ChatAPI:
    def __init__(self, parent: _MistralHTTPClient):
        self._parent = parent

    def complete(self, model: str, messages):
        data = self._parent._post(
            "/chat/completions",
            {"model": model, "messages": messages},
        )
        choices = []
        for choice in data.get("choices", []):
            choice_data = dict(choice)
            message = SimpleNamespace(**choice_data.pop("message", {}))
            choices.append(SimpleNamespace(message=message, **choice_data))
        return SimpleNamespace(choices=choices)


try:
    from mistralai import Mistral  # type: ignore

    client = Mistral(api_key=MISTRAL_API_KEY)
except Exception:
    client = _MistralHTTPClient(api_key=MISTRAL_API_KEY)