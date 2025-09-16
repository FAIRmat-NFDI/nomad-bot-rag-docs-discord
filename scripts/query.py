import logging
import os
from typing import List, Dict, Tuple, Set, Optional

import openai
import requests
from sentence_transformers import CrossEncoder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChromaDBRetriever:
    """
    Retrieves document chunks from a unified ChromaDB collection.
    """
    def __init__(self, collection):
        if not collection:
            raise ValueError("A valid ChromaDB collection object must be provided.")
        self.collection = collection
        logger.info(f"Successfully attached to collection: '{self.collection.name}'.")

    def retrieve(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Retrieves the top_k most relevant chunks from the collection."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        retrieved_chunks = [
            {
                'id': doc_id,
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            } for i, doc_id in enumerate(results['ids'][0])
        ]
        return retrieved_chunks

class RAGQueryEngine:
    """
    RAG engine using OpenAI chat (Completions) and OpenAI-compatible embeddings.
    All network settings can be overridden via environment variables.
    """

    def __init__(
        self,
        *,
        collection,                                   # REQUIRED: the Chroma collection
        openai_api_key: Optional[str] = None,
        openai_base_url: Optional[str] = None,        # default: https://api.openai.com/v1
        embedding_url: Optional[str] = None,          # default: <EMBED_BASE_URL>/v1/embeddings
        embedding_model: Optional[str] = None,        # default: text-embedding-3-large
        generator_model: Optional[str] = None,        # default: gpt-4o-mini
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        logger.info("Initializing RAG Query Engine with provided collection...")

        # --- Settings with sensible defaults (env overridable) ---
        self.openai_base_url = openai_base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        embed_base_url = os.getenv("EMBED_BASE_URL", "https://api.openai.com").rstrip("/")
        self.embedding_url = embedding_url or f"{embed_base_url}/v1/embeddings"
        self.embedding_model_name = embedding_model or os.getenv("EMBED_MODEL", "text-embedding-3-large")

        self.generator_model_name = generator_model or os.getenv("GENERATOR_MODEL", "gpt-4o-mini")

        # --- Components ---
        self.retriever = ChromaDBRetriever(collection=collection)

        try:
            self.client = OpenAI(api_key=self.openai_api_key, base_url=self.openai_base_url)
            logger.info(f"OpenAI client configured | base_url={self.openai_base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client. Error: {e}")
            raise

        try:
            self.reranker = CrossEncoder(reranker_model)
            logger.info(f"Reranker model '{reranker_model}' loaded successfully.")
        except Exception as e:
            logger.error(
                "Failed to load reranker model. Install sentence-transformers, "
                "or continue without reranking. Error: %s", e
            )
            self.reranker = None

    # -------- Embeddings (OpenAI-compatible /v1/embeddings) --------
    def _get_local_embedding(self, text: str) -> List[float]:
        """
        Gets a vector embedding via an OpenAI-compatible /v1/embeddings endpoint.
        Supports OpenAI cloud, LM Studio, vLLM, etc.
        """
        try:
            headers = {"Content-Type": "application/json"}
            if self.openai_api_key:
                headers["Authorization"] = f"Bearer {self.openai_api_key}"

            payload = {"model": self.embedding_model_name, "input": text}
            response = requests.post(self.embedding_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            # OpenAI format: {"data":[{"embedding":[...], "index":0, ...}], ...}
            if "data" in data and data["data"]:
                # sort to respect 'index' if batch was used
                items = sorted(data["data"], key=lambda x: x.get("index", 0))
                return items[0]["embedding"]

            # Some proxies might return {"embedding":[...]} or {"embeddings":[[...]]}
            if "embedding" in data:
                return data["embedding"]
            if "embeddings" in data and data["embeddings"]:
                return data["embeddings"][0]

            raise KeyError(f"Embedding not found in response. Got keys: {list(data.keys())}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling embeddings endpoint {self.embedding_url}: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected embeddings response: {e}. Body: {response.text[:500]}")
            raise

    # -------- Reranking --------
    def _rerank_chunks(self, query: str, chunks: List[Dict]) -> List[Dict]:
        if not self.reranker or not chunks:
            return chunks
        logger.info(f"Reranking {len(chunks)} chunks for relevance...")
        pairs = [[query, chunk["content"]] for chunk in chunks]
        scores = self.reranker.predict(pairs)
        for i in range(len(chunks)):
            chunks[i]["rerank_score"] = float(scores[i])
        return sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)

    # -------- Prompting --------
    def _prepare_messages(self, query: str, context_chunks: List[Dict]) -> List[Dict[str, str]]:
        context_str = "\n\n".join(
            f"Context {i+1}:\n{chunk['content']}" for i, chunk in enumerate(context_chunks)
        )
        system_prompt = """You are a helpful and friendly assistant specializing in NOMAD.
Answer based only on the provided context. Be clear, concise, and confident. If the
answer is not in the context, say you don't have that information."""
        user_prompt = f"""Here is the context retrieved from the knowledge base:
<context>
{context_str}
</context>

Based only on the context above, answer the following question:

Question: {query}
"""
        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    def _format_citations(self, chunks: List[Dict]) -> str:
        citation_set: Set[str] = set()
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            src = meta.get("source", "Unknown Source")
            citation_set.add(f"Source file: `{src}`")
        return "\n".join(f"- {c}" for c in sorted(citation_set)) or "No sources found."

    # -------- Generation --------
    def generate_answer(self, query: str, context_chunks: List[Dict]) -> str:
        messages = self._prepare_messages(query, context_chunks)
        try:
            logger.info("Generating answer via OpenAI chat...")
            response = self.client.chat.completions.create(
                model=self.generator_model_name,
                messages=messages,
                temperature=0.0,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            logger.error(f"Error during answer generation: {e}")
            return "Sorry, I encountered an error while generating the answer."

    # -------- End-to-end query --------
    def query(self, query: str, top_k: int = 5, rerank_top_n: int = 20) -> Tuple[str, str, List[Dict]]:
        logger.info(f"Received query: '{query}'")
        query_embedding = self._get_local_embedding(query)

        logger.info(f"Retrieving top {rerank_top_n} chunks for reranking...")
        retrieved_chunks = self.retriever.retrieve(query_embedding, top_k=rerank_top_n)

        reranked_chunks = self._rerank_chunks(query, retrieved_chunks)
        final_chunks = reranked_chunks[:top_k]
        logger.info(f"Selected top {len(final_chunks)} chunks after reranking.")

        answer = self.generate_answer(query, final_chunks)
        citations = self._format_citations(final_chunks)

        logger.info(f"Generated answer length: {len(answer)} chars")
        return answer, citations, final_chunks
