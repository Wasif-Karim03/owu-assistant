import time

from openai import OpenAI

from app.config import settings


class Embedder:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.EMBEDDING_MODEL

    def embed_single(self, text: str) -> list[float]:
        resp = self._client.embeddings.create(input=[text], model=self._model)
        return resp.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts with a small delay between API calls to stay
        under rate limits.  Texts are sent one-per-request so each response
        stays well within token limits for long chunks."""
        embeddings: list[list[float]] = []
        for i, text in enumerate(texts):
            resp = self._client.embeddings.create(input=[text], model=self._model)
            embeddings.append(resp.data[0].embedding)
            if i < len(texts) - 1:
                time.sleep(0.1)
        return embeddings
