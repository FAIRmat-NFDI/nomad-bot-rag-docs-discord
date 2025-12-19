# src/api/embeddings.py
import requests
from typing import List
from chromadb.utils.embedding_functions import EmbeddingFunction
from . import config

class LocalEmbeddingFunction(EmbeddingFunction):
    """A custom embedding function to connect to a local embedding model API."""

    def __init__(self, model_name=config.EMBED_MODEL_NAME):
        self.model_name = model_name
        self.base_url = config.EMBED_BASE_URL.rstrip("/")
        self.timeout = config.EMBED_TIMEOUT
        self.batch_size = max(1, config.EMBED_BATCH_SIZE)
        self._session = requests.Session()

    def _request_embeddings(self, batch: List[str]) -> List[List[float]]:
        try:
            resp = self._session.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model_name, "input": batch if len(batch) > 1 else batch[0]},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()

            if "embeddings" in data:
                embeddings = data["embeddings"]
            elif "embedding" in data and len(batch) == 1:
                embeddings = [data["embedding"]]
            else:
                raise RuntimeError(f"Unexpected embed response format: {data}")

            if len(embeddings) != len(batch):
                raise RuntimeError(
                    f"Embedding count mismatch. expected={len(batch)}, received={len(embeddings)}"
                )
            return embeddings
        except requests.RequestException as exc:
            print(f"Error calling embedding API: {exc}")
            raise

    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings: List[List[float]] = []
        for i in range(0, len(input), self.batch_size):
            batch = input[i : i + self.batch_size]
            if not batch:
                continue
            embeddings.extend(self._request_embeddings(batch))
        return embeddings

    def name(self) -> str:
        return f"local-embedding-{self.model_name}"
