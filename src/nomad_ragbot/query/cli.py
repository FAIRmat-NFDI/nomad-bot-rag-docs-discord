#!/usr/bin/env python3
import argparse
import os
import logging

# Make sure query.py is in the same directory or in the python path
try:
    from query import RAGQueryEngine
except ImportError:
    print("Error: Could not import RAGQueryEngine from query.py.")
    print("Please ensure query.py is in the same directory as cli.py.")
    exit(1)

# Configure basic logging for the CLI
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the command-line interface for the RAG Query Engine.
    """
    parser = argparse.ArgumentParser(
        description="A command-line interface for the NOMAD RAG chatbot.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # --- Connection and Model Arguments ---
    parser.add_argument(
        "--chromadb-host",
        default=os.getenv("CHROMADB_HOST", "localhost"),
        help="Hostname for the ChromaDB server."
    )
    parser.add_argument(
        "--chromadb-port",
        type=int,
        default=os.getenv("CHROMADB_PORT", 8000),
        help="Port for the ChromaDB server."
    )
    parser.add_argument(
        "--collection",
        default=os.getenv("CHROMADB_COLLECTION", "nomad_knowledge"),
        help="Name of the ChromaDB collection to query."
    )
    parser.add_argument(
        "--openai-base-url",
        default=os.getenv("OPENAI_BASE_URL", "http://172.28.105.142:11434/v1"),
        help="Base URL for the OpenAI-compatible chat API."
    )
    parser.add_argument(
        "--embedding-url",
        default=os.getenv("EMBEDDING_URL", "http://172.28.105.142:11434/api/embed"),
        help="URL for the custom local embedding model endpoint."
    )
    parser.add_argument(
        "--embedding-model",
        default=os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
        help="Name of the embedding model."
    )
    parser.add_argument(
        "--generator-model",
        default=os.getenv("GENERATOR_MODEL", "gpt-oss:20b"),
        help="Name of the generator (chat) model."
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY", "not-needed"),
        help="API key for the service (if required)."
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of relevant chunks to retrieve for context."
    )

    args = parser.parse_args()

    try:
        engine = RAGQueryEngine(
            chromadb_host=args.chromadb_host,
            chromadb_port=args.chromadb_port,
            # Note: The collection name is handled inside the retriever in query.py
            # If you need to make it configurable here, you'd pass it down.
            openai_api_key=args.api_key,
            openai_base_url=args.openai_base_url,
            embedding_url=args.embedding_url,
            embedding_model=args.embedding_model,
            generator_model=args.generator_model
        )
    except Exception as e:
        logger.error(f"Failed to initialize the RAG engine: {e}")
        return

    print("\n🤖 NOMAD RAG Chatbot CLI")
    print("="*30)
    print("Ask a question about the NOMAD documentation.")
    print("Type 'exit' or 'quit' to end the chat.\n")

    while True:
        try:
            user_query = input("You: ")
            if user_query.strip().lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!")
                break

            if not user_query.strip():
                continue

            answer, citations, _ = engine.query(user_query, top_k=args.top_k)

            print("\n" + "─"*50)
            print(f"🤖 Answer:\n{answer}")
            print("\n" + "─"*20)
            print(f"📚 Sources:\n{citations}")
            print("─"*50 + "\n")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"An error occurred during query: {e}")
            print("An unexpected error occurred. Please try again.")


if __name__ == "__main__":
    main()