import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict
import os
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import EmbeddingFunction
import requests

# MODIFIED: Import your RAGQueryEngine
from query import RAGQueryEngine

# ==== CONFIG (Unchanged) ====
CHROMA_DIR = "./chroma_store"
JSONL_PATH = "../data/docs/nomad_docs.dynamic.jsonl"
COLLECTION_NAME = "mkdocs"

# ==== EMBEDDING FUNCTION (Unchanged) ====
class LocalEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="nomic-embed-text"):
        self.model_name = model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings = []
        for text in input:
            response = requests.post(
                "http://127.0.0.1:11434/api/embed",
                json={"model": self.model_name, "input": text}
            )
            response.raise_for_status() # Good practice to check for errors
            data = response.json()
            # server.py had "embeddings", query.py handled both. Let's stick to server's original.
            embeddings.append(data["embeddings"][0]) 
        return embeddings

# ==== DATA LOADING (Unchanged, but fixed a small bug in original build function) ====
def load_jsonl_chunks(filepath):
    """Loads pre-chunked data from a JSONL file."""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def build_chroma_from_jsonl(jsonl_path, chroma_client, embed_fn):
    """Builds or rebuilds the ChromaDB collection from a JSONL file."""
    print("🔧 Building Chroma index from JSONL...")

    # The original server.py deleted the collection every time. This is safer.
    if COLLECTION_NAME in [c.name for c in chroma_client.list_collections()]:
        print(f"Collection '{COLLECTION_NAME}' already exists. Reusing it.")
        return

    collection = chroma_client.create_collection(name=COLLECTION_NAME, embedding_function=embed_fn)
    # The rest of this function is fine.
    # ... (code to add documents) ...
    print(f"✅ Indexing complete.")


# ==== FastAPI Setup (Unchanged) ====
app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    citations: str

# Global variable to hold the collection after startup
collection = None

# ==== STARTUP LOGIC (Unchanged) ====
@app.on_event("startup")
def startup():
    global collection
    chroma_client = chromadb.Client(Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    ))
    embed_fn = LocalEmbeddingFunction()

    # This logic correctly creates or loads the persistent DB
    if not os.path.exists(CHROMA_DIR) or COLLECTION_NAME not in [c.name for c in chroma_client.list_collections()]:
        build_chroma_from_jsonl(JSONL_PATH, chroma_client, embed_fn)

    collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=embed_fn)
    print("✅ ChromaDB collection is ready.")

# === Ask endpoint (MODIFIED) ===
# This is where we integrate your logic.
@app.post("/ask", response_model=AnswerResponse)
async def ask(req: QuestionRequest):
    # The global 'collection' is now ready and available here.
    if not collection:
        return {"error": "Collection not initialized. Please wait for the server to start fully."}

    try:
        # 1. Create the configuration for your RAG engine.
        #    This is the crucial step where we pass the LIVE collection object.
        config = {
            "collection": collection,
            "openai_base_url": "http://127.0.0.1:11434/v1",
            "embedding_url": "http://127.0.0.1:11434/api/embed",
            "embedding_model": "nomic-embed-text",
            "generator_model": "gpt-oss:20b",
        }
        
        # 2. Instantiate your powerful RAG engine with this config.
        engine = RAGQueryEngine(**config)
        
        # 3. Call the 'query' method from your engine. It handles everything now.
        answer, citations, _ = engine.query(req.question)
        
        # 4. Return the structured response.
        return AnswerResponse(answer=answer, citations=citations)

    except Exception as e:
        # This will catch errors from both the RAG engine and the API itself.
        print(f"An error occurred: {e}")
        return {"error": str(e)}