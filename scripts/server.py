# scripts/server.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
import requests

from openai import OpenAI
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import EmbeddingFunction

# keep if your RAG engine uses it
from query import RAGQueryEngine

# ==== CONFIG ====
CHROMA_DIR = "./chroma_store"

# NOTE: point this at your dynamic JSONL
JSONL_PATH = "../data/chunks/docs.dynamic.jsonl"
COLLECTION_NAME = "mkdocs"

# ==== EMBEDDING FUNCTION ====
class LocalEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="nomic-embed-text"):
        self.model_name = model_name
        self.base_url = os.getenv("EMBED_BASE_URL", "http://172.28.105.142:11434")
        self.timeout = int(os.getenv("EMBED_TIMEOUT", "20"))
        self._session = requests.Session()

    def __call__(self, input: List[str]) -> List[List[float]]:
        embs = []
        for text in input:
            r = self._session.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model_name, "input": text},
                timeout=self.timeout,
            )
            r.raise_for_status()
            data = r.json()
            # supports {"embeddings":[[...]]} or {"embedding":[...]}
            if "embeddings" in data and data["embeddings"]:
                embs.append(data["embeddings"][0])
            elif "embedding" in data:
                embs.append(data["embedding"])
            else:
                raise RuntimeError(f"Unexpected embed response: {data}")
        return embs

    def name(self) -> str:
        return f"sentence-transformers-{self.model_name}"

# ==== HELPERS YOU ASKED TO RESTORE ====

def load_jsonl_chunks(filepath: str):
    """Yield JSON objects from a JSONL file, skipping blank lines."""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

def _sanitize_metadata(d: dict) -> dict:
    """
    Chroma Rust backend allows only primitive values (str|int|float|bool).
    Drop None; stringify non-primitives.
    """
    out = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out

def _make_unique_id(rid: str, item: dict, seen: set, counter: int) -> str:
    """
    Ensure IDs are unique; if duplicate, append a stable suffix derived from
    (id, path, source, section). Falls back to counter if necessary.
    """
    if rid not in seen:
        return rid
    path = item.get("path") or item.get("path_normalized") or item.get("path_original") or ""
    src  = item.get("source") or ""
    sec  = item.get("section") or ""
    base = f"{rid}|{path}|{src}|{sec}"
    suffix = abs(hash(base)) % (10**8)
    cand = f"{rid}::{suffix}"
    while cand in seen:
        counter += 1
        cand = f"{rid}::{suffix}-{counter}"
    return cand

# ==== BUILD CHROMA FROM JSONL (uses restored helpers) ====

def build_chroma_from_jsonl(jsonl_path, chroma_client, embed_fn):
    print("🔧 Building Chroma index from JSONL...")

    # # The original server.py deleted the collection every time. This is (apparently) safer. Check before merging
    if COLLECTION_NAME in [c.name for c in chroma_client.list_collections()]:
        print(f"Collection '{COLLECTION_NAME}' already exists. Reusing it.")
        return

    collection = chroma_client.create_collection(
        name="mkdocs",
        embedding_function=embed_fn
    )

    ids, documents, metadatas = [], [], []
    seen_ids = set()
    count = 0

    for item in load_jsonl_chunks(jsonl_path):
        text = item.get("text")
        if not text or not str(text).strip():
            continue

        raw_id = str(item.get("id") or f"chunk_{count}")
        rid = _make_unique_id(raw_id, item, seen_ids, count)
        seen_ids.add(rid)

        # Your dynamic JSONL has "source" (full URL). Older field "url" is usually absent.
        meta_raw = {
            "source": item.get("source"),  # canonical link
            "title": item.get("title"),
            "section": item.get("section"),
            "timestamp": item.get("timestamp"),
            # optional extras if present:
            "repo": item.get("repo"),
            "path": item.get("path") or item.get("path_normalized") or item.get("path_original"),
        }
        meta = _sanitize_metadata(meta_raw)

        ids.append(rid)
        documents.append(str(text))
        metadatas.append(meta)
        count += 1

    if not ids:
        raise RuntimeError(f"No valid records found in {jsonl_path}")

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"✅ Indexed {count} chunks from JSONL.")
    return collection

# (kept for compatibility; not used by /ask since you call RAGQueryEngine)
def retrieve_context(query, collection, top_k=3):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results['documents'][0] if results['documents'] else []

# ==== FastAPI Setup ====
app = FastAPI()
client = OpenAI(
    base_url="http://172.28.105.142:11434/v1",
    api_key="not-needed"
)

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    rerank_top_n: Optional[int] = 20

class AnswerResponse(BaseModel):
    answer: str
    citations: str

# Global variable to hold the collection after startup
collection = None

# Memory (global for now)
chat_history: List[Dict[str, str]] = [
    {"role": "system", "content": "You are a helpful assistant that answers questions about the MkDocs documentation files provided in context."}
]

@app.on_event("startup")
def startup():
    global collection
    chroma_client = chromadb.Client(Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    ))
    embed_fn = LocalEmbeddingFunction()

    # build only if missing; else reuse persisted store
    if not os.path.exists(CHROMA_DIR) or "mkdocs" not in [c.name for c in chroma_client.list_collections()]:
        build_chroma_from_jsonl(JSONL_PATH, chroma_client, embed_fn)

    collection = chroma_client.get_collection(name="mkdocs", embedding_function=embed_fn)

# === Ask endpoint ===
@app.post("/ask", response_model=AnswerResponse)
async def ask(req: QuestionRequest):
    if not collection:
        # collection should be set in startup; guard just in case
        return {"error": "Collection not initialized. Please wait for the server to start fully."}

    try:
        # Configure your RAGQueryEngine with the live collection
        config = {
            "collection": collection,
            "openai_base_url": "http://172.28.105.142:11434/v1",
            "embedding_url": "http://172.28.105.142:11434/api/embed",
            "embedding_model": "nomic-embed-text",
            "generator_model": "gpt-oss:20b",
            "reranker_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        }

        engine = RAGQueryEngine(**config)
        answer, citations, _ = engine.query(
            req.question,
            top_k=req.top_k,
            rerank_top_n=req.rerank_top_n
        )

        return AnswerResponse(answer=answer, citations=citations)

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}