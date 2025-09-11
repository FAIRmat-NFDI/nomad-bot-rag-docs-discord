#!/usr/bin/env python3
"""
A conversational workflow for the NOMAD RAG chatbot.

This script manages the user interaction and conversation memory. It uses the
RAGQueryEngine from query.py to handle the complexities of retrieval,
prompting, and answer generation for each turn of the conversation.
"""
import logging
from query import RAGQueryEngine


# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def chat_loop(engine: RAGQueryEngine):
    """
    Manages the interactive chat loop, including conversation memory.

    Args:
        engine: An initialized instance of the RAGQueryEngine.
    """
    print("🤖 Ask me anything about the NOMAD documentation! Type 'exit' to quit.\n")
    
    messages = [{
        "role": "system",
        "content": "You are a helpful and friendly assistant for NOMAD."
    }]

    while True:
        user_input = input("💬 You: ")
        if user_input.strip().lower() in ['exit', 'quit']:
            print("👋 Exiting chat.")
            break

        if not user_input.strip():
            continue

        try:
            answer, citations, _ = engine.query(user_input)
            
            # Format the final response to show the user
            final_response = f"{answer}\n\n---\n*Sources:*\n{citations}"
            print(f"\n🤖 {final_response}\n")

            # --- This is the memory mechanism from chatbot.py ---
            # We append the clean user input and the final AI response to our history.
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": final_response})

        except Exception as e:
            logger.error(f"An error occurred during the query: {e}", exc_info=True)
            print(f"\n❌ An error occurred. Please try again. Error: {e}\n")


def main():
    """
    Initializes the RAG engine and starts the chat loop.
    """
    # --- Configuration for the RAGQueryEngine ---
    # These settings point to your local models and the ChromaDB server.
    config = {
        "chromadb_host": "localhost",
        "chromadb_port": 8000,
        "openai_base_url": "http://172.28.105.142:11434/v1",
        "embedding_url": "http://172.28.105.142:11434/api/embed",
        "embedding_model": "nomic-embed-text",
        "generator_model": "gpt-oss:20b",
        "openai_api_key": "not-needed"
    }

    try:
        # Initialize the RAG engine with our configuration.
        engine = RAGQueryEngine(**config)
    except Exception as e:
        logger.error(f"Failed to initialize the RAG engine: {e}")
        print("\n❌ Could not connect to backend services (ChromaDB or AI models).")
        print("Please ensure ChromaDB is running as a server and the model endpoints are correct.")
        return

    # Start the conversation
    chat_loop(engine)


if __name__ == "__main__":
    main()