# src/api/embeddings.py
import requests
from typing import List
from chromadb.utils.embedding_functions import EmbeddingFunction
from . import config

class LocalEmbeddingFunction(EmbeddingFunction):
    """A custom embedding function to connect to a local embedding model API."""
    def __init__(self, model_name=config.EMBED_MODEL_NAME):
        self.model_name = model_name
        self.base_url = config.EMBED_BASE_URL
        self.timeout = config.EMBED_TIMEOUT
        self._session = requests.Session()

    def __call__(self, input: List[str]) -> List[List[float]]:
        embs = []
        for text in input:
            try:
                r = self._session.post(
                    f"{self.base_url}/api/embed",
                    json={"model": self.model_name, "input": text},
                    timeout=self.timeout,
                )
                r.raise_for_status()
                data = r.json()

                # Supports both {"embeddings":[[...]]} and {"embedding":[...]} formats
                if "embeddings" in data and data["embeddings"]:
                    embs.append(data["embeddings"][0])
                elif "embedding" in data:
                    embs.append(data["embedding"])
                else:
                    raise RuntimeError(f"Unexpected embed response format: {data}")
            except requests.RequestException as e:
                print(f"Error calling embedding API: {e}")
                raise
        return embs

    def name(self) -> str:
        return f"local-embedding-{self.model_name}"
