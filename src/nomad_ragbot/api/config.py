import os

# --- Directory and File Paths ---
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_store")
JSONL_PATH = os.getenv("JSONL_PATH", "data/chunks/docs.dynamic.jsonl")

# --- Embedding Model Configuration ---
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "http://172.28.105.142:11434")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "nomic-embed-text")
EMBED_TIMEOUT = int(os.getenv("EMBED_TIMEOUT", "20"))

# --- OpenAI-Compatible API Configuration ---
GENERATOR_BASE_URL = os.getenv("GENERATOR_BASE_URL", "http://172.28.105.142:11434/v1")
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "gpt-oss:20b")

# --- Reranker Configuration ---
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# --- ChromaDB Collection Name ---
COLLECTION_NAME = "mkdocs"

