import logging
import os
from typing import List, Dict, Tuple, Set

# import chromadb # No longer needed here
import openai
import requests
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChromaDBRetriever:
    """
    Retrieves document chunks from a unified ChromaDB collection.
    """
    # MODIFIED: The __init__ method now accepts a pre-initialized collection object.
    def __init__(self, collection):
        if not collection:
            raise ValueError("A valid ChromaDB collection object must be provided.")
        self.collection = collection
        logger.info(f"Successfully attached to collection: '{self.collection.name}'.")

    def retrieve(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Retrieves the top_k most relevant chunks from the collection."""
        # This method is unchanged and works perfectly.
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
    A RAG engine using a local OpenAI-compatible API for chat and a custom endpoint for embeddings.
    """
    # MODIFIED: The __init__ method now accepts the 'collection' object directly.
    def __init__(self,
                 collection,  # This is the key change!
                 openai_api_key: str = "not-needed",
                 openai_base_url: str = "http://127.0.0.1:11434/v1",
                 embedding_url: str = "http://127.0.0.1:11434/api/embed",
                 embedding_model: str = "nomic-embed-text",
                 generator_model: str = "gpt-oss:20b"):
        """
        Initializes the RAGQueryEngine.
        """
        logger.info("Initializing RAG Query Engine with provided collection...")
        # MODIFIED: Pass the provided collection object to the retriever.
        self.retriever = ChromaDBRetriever(collection=collection)
        
        # Configure OpenAI client for the CHAT model (this part is unchanged)
        try:
            self.client = openai.OpenAI(api_key=openai_api_key, base_url=openai_base_url)
            self.generator_model_name = generator_model
            logger.info(f"OpenAI chat client configured for base URL: {openai_base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client. Error: {e}")
            raise

        # Store config for the custom EMBEDDING model endpoint (this part is unchanged)
        self.embedding_url = embedding_url
        self.embedding_model_name = embedding_model
        logger.info(f"Custom embedding endpoint configured for URL: {self.embedding_url}")

    # --- ALL OTHER METHODS BELOW THIS LINE ARE UNCHANGED ---
    # They will now use the collection that was passed in.

    def _get_local_embedding(self, text: str) -> List[float]:
        """
        Gets a vector embedding from a local, custom model server.
        """
        try:
            response = requests.post(
                self.embedding_url,
                json={"model": self.embedding_model_name, "input": text},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            if 'embedding' in data:
                 return data['embedding']
            elif 'embeddings' in data:
                 return data['embeddings'][0]
            else:
                 raise KeyError("Embedding not found in response from server.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling embedding endpoint: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response structure from embedding endpoint: {e}. Response: {response.text}")
            raise

    def _prepare_messages(self, query: str, context_chunks: List[Dict]) -> List[Dict[str, str]]:
        """Creates the message structure for the OpenAI Chat Completions API."""
        context_str = "\n\n".join(f"Context {i+1}:\n{chunk['content']}" for i, chunk in enumerate(context_chunks))
        system_prompt = """You are a helpful and friendly assistant specializing in NOMAD, a platform for managing and sharing materials science data. Your goal is to provide clear, accurate, and concise answers based on the provided context.

IMPORTANT GUIDELINES:
1.  Your primary goal is to answer the user's question accurately based *only* on the provided context.
2.  Do NOT mention the context, the documentation, or "the information provided" in your answer. Just answer the question directly.
3.  If the context does not contain the answer, state that you don't have enough information to answer the question. Do not make up information.
4.  Be friendly, conversational, and direct in your tone.
"""
        user_prompt = f"""Here is the context retrieved from the knowledge base:
<context>
{context_str}
</context>

Based *only* on the context above, please answer the following question.

Question: {query}
"""
        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    def _format_citations(self, chunks: List[Dict]) -> str:
        """Formats the citation string from the metadata of retrieved chunks."""
        citation_set: Set[str] = set()
        for chunk in chunks:
            meta = chunk.get('metadata', {})
            source_path = meta.get('source', 'Unknown Source')
            citation_set.add(f"Source file: `{source_path}`")
        return "\n".join(f"- {citation}" for citation in sorted(list(citation_set))) or "No sources found."

    def generate_answer(self, query: str, context_chunks: List[Dict]) -> str:
        """Generates an answer using the OpenAI Chat Completions API."""
        messages = self._prepare_messages(query, context_chunks)
        try:
            logger.info("Generating answer via local chat model...")
            response = self.client.chat.completions.create(
                model=self.generator_model_name,
                messages=messages,
                temperature=0.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during answer generation with local chat model: {e}")
            return "Sorry, I encountered an error while generating the answer."

    def query(self, query: str, top_k: int = 5) -> Tuple[str, str, List[Dict]]:
        """Performs a full RAG query and returns answer, citations, and chunks."""
        logger.info(f"--- Starting new query pipeline for: '{query}' ---")
        total_start_time = time.perf_counter()

        embed_start_time = time.perf_counter()
        query_embedding = self._get_local_embedding(query)
        embed_latency = time.perf_counter() - embed_start_time
        logger.info(f"[Latency] Embedding generation: {embed_latency:.4f}s")
        
        retrieval_start_time = time.perf_counter()        
        relevant_chunks = self.retriever.retrieve(query_embedding, top_k=top_k)
        retrieval_latency = time.perf_counter() - retrieval_start_time        
        logger.info(f"[Latency] Chunk retrieval: {retrieval_latency:.4f}s")        
        
        answer_start_time = time.perf_counter()        
        answer = self.generate_answer(query, relevant_chunks)
        answer_latency = time.perf_counter() - answer_start_time        
        logger.info(f"[Latency] Answer generation: {answer_latency:.4f}s")        
        
        logger.info(f"--- Formatting citations for: '{query}' ---")        
        citations = self._format_citations(relevant_chunks)
        logger.info(f"Generated answer: '{answer}'")

        total_latency = time.perf_counter() - total_start_time
        logger.info(f"--- Total query pipeline finished in {total_latency:.4f}s ---")
        
        return answer, citations, relevant_chunks