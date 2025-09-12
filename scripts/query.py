import logging
import os
from typing import List, Dict, Tuple, Set

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
    A RAG engine using a local OpenAI-compatible API for chat and a custom endpoint for embeddings.
    """
    def __init__(self,
                 collection,  # This is the key change!
                 openai_api_key: str = "not-needed",
                 openai_base_url: str = "http://127.0.0.1:11434/v1",
                 embedding_url: str = "http://127.0.0.1:11434/api/embed",
                 embedding_model: str = "nomic-embed-text",
                 generator_model: str = "gpt-oss:20b",
                 reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initializes the RAGQueryEngine.
        """
        logger.info("Initializing RAG Query Engine with provided collection...")

        self.retriever = ChromaDBRetriever(collection=collection)

        try:
            self.client = openai.OpenAI(api_key=openai_api_key, base_url=openai_base_url)
            self.generator_model_name = generator_model
            logger.info(f"OpenAI chat client configured for base URL: {openai_base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client. Error: {e}")
            raise

        self.embedding_url = embedding_url
        self.embedding_model_name = embedding_model
        logger.info(f"Custom embedding endpoint configured for URL: {self.embedding_url}")

        try:
            self.reranker = CrossEncoder(reranker_model)
            logger.info(f"Reranker model '{reranker_model}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load reranker model. Please run 'pip install sentence-transformers'. Error: {e}")
            self.reranker = None

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

    def _rerank_chunks(self, query: str, chunks: List[Dict]) -> List[Dict]:
        """Reranks retrieved chunks for better relevance using a cross-encoder."""
        if not self.reranker or not chunks:
            return chunks

        logger.info(f"Reranking {len(chunks)} chunks for relevance...")
        # Create pairs of [query, chunk_content] for the cross-encoder to score.
        pairs = [[query, chunk['content']] for chunk in chunks]
        
        # Predict the relevance scores.
        scores = self.reranker.predict(pairs)
        
        # Add the scores to the chunks and sort them.
        for i in range(len(chunks)):
            chunks[i]['rerank_score'] = scores[i]
            
        # Sort chunks by the new rerank score in descending order (higher is better).
        sorted_chunks = sorted(chunks, key=lambda x: x['rerank_score'], reverse=True)
        
        return sorted_chunks

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

    def query(self, query: str, top_k: int = 5, rerank_top_n: int = 20) -> Tuple[str, str, List[Dict]]:
        """
        Performs a full RAG query: embed, retrieve, rerank, and generate.

        Args:
            query: The user's question.
            top_k: The final number of chunks to use for the answer.
            rerank_top_n: The number of chunks to retrieve initially for reranking.
        """
        logger.info(f"Received query: '{query}'")
        query_embedding = self._get_local_embedding(query)
        
        # STEP 1: Retrieve a larger number of chunks for the reranker.
        logger.info(f"Retrieving top {rerank_top_n} chunks for reranking...")
        retrieved_chunks = self.retriever.retrieve(query_embedding, top_k=rerank_top_n)
        
        # STEP 2: Rerank the retrieved chunks to find the most relevant ones.
        reranked_chunks = self._rerank_chunks(query, retrieved_chunks)
        
        # STEP 3: Select the final top_k chunks to be used as context.
        final_chunks = reranked_chunks[:top_k]
        logger.info(f"Selected top {len(final_chunks)} chunks after reranking.")
        
        # The rest of the process uses the higher-quality, reranked context.
        answer = self.generate_answer(query, final_chunks)
        
        logger.info("Formatting citations...")
        citations = self._format_citations(final_chunks)
        
        logger.info(f"Generated answer: '{answer}'")
        return answer, citations, final_chunks