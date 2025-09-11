import logging
import os
from typing import List, Dict, Tuple, Set

import chromadb
import openai
import requests  # Import the requests library for local embeddings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChromaDBRetriever:
    """
    Retrieves document chunks from a unified ChromaDB collection.
    """
    def __init__(self, host: str = "localhost", port: int = 8000, collection_name: str = "nomad_knowledge"):
        try:
            # Assuming Chroma is running locally as a server, not persisted to disk
            self.client = chromadb.HttpClient(host=host, port=port)
            self.client.heartbeat()
            logger.info(f"Successfully connected to ChromaDB at {host}:{port}.")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB. Please ensure it is running. Error: {e}")
            raise ConnectionError("Could not connect to ChromaDB.") from e

        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"Successfully retrieved collection: '{collection_name}'.")
        except Exception as e:
            # Note: The embedding function must match the one used to create the collection.

            logger.warning(f"Failed to get collection '{collection_name}'. Error: {e}")
            raise ValueError(f"Collection '{collection_name}' not found.") from e

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
                 chromadb_host: str = "localhost",
                 chromadb_port: int = 8000,
                 openai_api_key: str = "not-needed",
                 openai_base_url: str = "http://172.28.105.142:11434/v1",
                 embedding_url: str = "http://172.28.105.142:11434/api/embed",
                 embedding_model: str = "nomic-embed-text",
                 generator_model: str = "gpt-oss:20b"):
        """
        Initializes the RAGQueryEngine with specific endpoints from chatbot.py.
        """
        logger.info("Initializing RAG Query Engine with local model configuration...")
        self.retriever = ChromaDBRetriever(host=chromadb_host, port=chromadb_port)
        
        # Configure OpenAI client for the CHAT model
        try:
            self.client = openai.OpenAI(api_key=openai_api_key, base_url=openai_base_url)
            self.generator_model_name = generator_model
            logger.info(f"OpenAI chat client configured for base URL: {openai_base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client. Error: {e}")
            raise

        # Store config for the custom EMBEDDING model endpoint
        self.embedding_url = embedding_url
        self.embedding_model_name = embedding_model
        logger.info(f"Custom embedding endpoint configured for URL: {self.embedding_url}")

    def _get_local_embedding(self, text: str) -> List[float]:
        """
        Gets a vector embedding from a local, custom model server.
        This mimics the logic from chatbot.py's LocalEmbeddingFunction.
        """
        try:
            response = requests.post(
                self.embedding_url,
                json={
                    "model": self.embedding_model_name,
                    "input": text
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            # The original script had a typo 'embed', but based on the class it was likely 'embedding'
            # I'll check for both for robustness
            if 'embedding' in data:
                 return data['embedding']
            elif 'embeddings' in data: # The original class had this typo
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
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

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
                temperature=0.0, # Set to 0 for deterministic, factual answers
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during answer generation with local chat model: {e}")
            return "Sorry, I encountered an error while generating the answer."

    def query(self, query: str, top_k: int = 5) -> Tuple[str, str, List[Dict]]:
        """Performs a full RAG query and returns answer, citations, and chunks."""
        logger.info(f"Received query: '{query}'")
        
        query_embedding = self._get_local_embedding(query)
        
        logger.info("Retrieving relevant chunks from ChromaDB...")
        relevant_chunks = self.retriever.retrieve(query_embedding, top_k=top_k)
        
        answer = self.generate_answer(query, relevant_chunks)
        
        logger.info("Formatting citations...")
        citations = self._format_citations(relevant_chunks)
        
        logger.info(f"Generated answer: '{answer}'")
        return answer, citations, relevant_chunks

# This block allows you to run the script directly for testing
if __name__ == '__main__':
    # Configuration from your chatbot.py script
    CHAT_BASE_URL = "http://172.28.105.142:11434/v1"
    EMBEDDING_URL = "http://172.28.105.142:11434/api/embed"
    EMBEDDING_MODEL = "nomic-embed-text"
    GENERATOR_MODEL = "gpt-oss:20b"
    API_KEY = "not-needed" 

    try:
        engine = RAGQueryEngine(
            openai_api_key=API_KEY,
            openai_base_url=CHAT_BASE_URL,
            embedding_url=EMBEDDING_URL,
            embedding_model=EMBEDDING_MODEL,
            generator_model=GENERATOR_MODEL
        )
        user_query = "How do I upload a new entry to NOMAD?"
        
        final_answer, final_citations, retrieved_chunks = engine.query(user_query)
        
        print("\n" + "="*50)
        print(f"Query: {user_query}")
        print("\n" + "="*50)
        print(f"Answer:\n{final_answer}")
        print("\n" + "-"*50)
        print(f"Sources:\n{final_citations}")
        print("\n" + "="*50)

    except (ConnectionError, ValueError) as e:
        logger.error(f"Could not run RAG engine example: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")