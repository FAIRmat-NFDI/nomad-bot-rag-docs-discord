import logging
import os
from typing import List, Dict, Tuple, Set

import chromadb
import openai  # Import the OpenAI library

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChromaDBRetriever:
    """
    Retrieves document chunks from a unified ChromaDB collection.
    """
    def __init__(self, host: str = "localhost", port: int = 8000, collection_name: str = "nomad_knowledge"):
        try:
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
            logger.error(f"Failed to get collection '{collection_name}'. Please ensure it exists. Error: {e}")
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
    A RAG engine using an OpenAI-compatible API for embeddings and generation.
    """
    def __init__(self,
                 chromadb_host: str = "localhost",
                 chromadb_port: int = 8000,
                 openai_api_key: str = "YOUR_API_KEY_HERE",
                 openai_base_url: str = "http://localhost:8000/v1",
                 embedding_model: str = "text-embedding-ada-002",
                 generator_model: str = "gpt-3.5-turbo"):
        """
        Initializes the RAGQueryEngine.

        Args:
            openai_api_key: Your OpenAI API key (or a placeholder for local models).
            openai_base_url: The base URL of your local OpenAI-compatible server.
            embedding_model: The name/ID of the embedding model to use.
            generator_model: The name/ID of the generator model to use.
        """
        logger.info("Initializing RAG Query Engine with OpenAI-compatible models...")
        self.retriever = ChromaDBRetriever(host=chromadb_host, port=chromadb_port)
        
        try:
            self.client = openai.OpenAI(api_key=openai_api_key, base_url=openai_base_url)
            self.embedding_model_name = embedding_model
            self.generator_model_name = generator_model
            logger.info(f"OpenAI client configured for base URL: {openai_base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client. Error: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """Generates a vector embedding for the given text using the OpenAI API."""
        try:
            text = text.replace("\n", " ")
            response = self.client.embeddings.create(model=self.embedding_model_name, input=[text])
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding with OpenAI API: {e}")
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
            source = meta.get('source')
            if source == 'mkdocs':
                url = meta.get('url', 'No URL found')
                citation_set.add(f"[Documentation Page]({url})")
            elif source == 'discord':
                author = meta.get('author', 'Unknown User')
                message_url = meta.get('message_url', '#')
                citation_set.add(f"[Discord message by {author}]({message_url})")

        return "\n".join(f"- {citation}" for citation in sorted(list(citation_set))) or "No sources found."

    def generate_answer(self, query: str, context_chunks: List[Dict]) -> str:
        """Generates an answer using the OpenAI Chat Completions API."""
        messages = self._prepare_messages(query, context_chunks)
        
        try:
            logger.info("Generating answer via OpenAI compatible API...")
            response = self.client.chat.completions.create(
                model=self.generator_model_name,
                messages=messages,
                temperature=0.2, # Lower temperature for more factual answers
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during answer generation with OpenAI API: {e}")
            return "Sorry, I encountered an error while generating the answer."

    def query(self, query: str, top_k: int = 5) -> Tuple[str, str, List[Dict]]:
        """Performs a full RAG query and returns answer, citations, and chunks."""
        logger.info(f"Received query: '{query}'")
        
        query_embedding = self.generate_embedding(query)
        
        logger.info("Retrieving relevant chunks from ChromaDB...")
        relevant_chunks = self.retriever.retrieve(query_embedding, top_k=top_k)
        
        answer = self.generate_answer(query, relevant_chunks)
        
        logger.info("Formatting citations...")
        citations = self._format_citations(relevant_chunks)
        
        logger.info(f"Generated answer: '{answer}'")
        return answer, citations, relevant_chunks

# This block allows you to run the script directly for testing
if __name__ == '__main__':
    # It's recommended to set these as environment variables
    API_KEY = os.getenv("OPENAI_API_KEY", "not-needed-for-local")
    BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1")
    EMBEDDING_MODEL = "your-local-embedding-model-name"  # e.g., "mxbai-embed-large-v1"
    GENERATOR_MODEL = "your-local-generator-model-name"  # e.g., "llama3-8b-instruct"

    try:
        engine = RAGQueryEngine(
            openai_api_key=API_KEY,
            openai_base_url=BASE_URL,
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