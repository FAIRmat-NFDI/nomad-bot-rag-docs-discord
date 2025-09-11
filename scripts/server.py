from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict
import os
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import EmbeddingFunction
from markdown import markdown
from bs4 import BeautifulSoup
import requests

# ==== CONFIG ====
DOCS_DIR = "./docs"
CHROMA_DIR = "./chroma_store"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ==== EMBEDDING FUNCTION ====
class LocalEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="nomic-embed-text"):
        self.model_name = model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings = []
        for text in input:
            response = requests.post(
                "http://172.28.105.142:11434/api/embed",
                json={"model": self.model_name, "input": text}
            )
            data = response.json()
            embeddings.append(data["embeddings"][0])
        return embeddings

    def name(self) -> str:
        return f"sentence-transformers-{self.model_name}"

import json

def load_jsonl_chunks(filepath):
    """
    Load pre-chunked data from a JSONL file.
    Each line is expected to be a valid JSON object with keys like:
    id, text, source, title, section, url, timestamp
    """
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def build_chroma_from_jsonl(jsonl_path, chroma_client, embed_fn):
    print("🔧 Building Chroma index from JSONL...")

    if "mkdocs" in [c.name for c in chroma_client.list_collections()]:
        chroma_client.delete_collection("mkdocs")

    collection = chroma_client.create_collection(name="mkdocs", embedding_function=embed_fn)

    count = 0
    for item in load_jsonl_chunks(jsonl_path):
        text = item.get("text", "")
        if not text.strip():
            continue

def _sanitize_metadata(d: dict) -> dict:
    out = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out

def load_jsonl_chunks(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

def _make_unique_id(rid: str, item: dict, seen: set[int | str], counter: int) -> str:
    """Ensure ID uniqueness; append a deterministic suffix if needed."""
    if rid not in seen:
        return rid
    # Prefer stable components to avoid flapping across runs
    path = item.get("path") or item.get("path_normalized") or item.get("path_original") or ""
    src  = item.get("source") or ""
    sec  = item.get("section") or ""
    # Short hash-like suffix
    base = f"{rid}|{path}|{src}|{sec}"
    suffix = abs(hash(base)) % (10**8)
    cand = f"{rid}::{suffix}"
    # If by any chance still collides, fall back to counter
    while cand in seen:
        counter += 1
        cand = f"{rid}::{suffix}-{counter}"
    return cand

def build_chroma_from_jsonl(jsonl_path, chroma_client, embed_fn):
    print("🔧 Building Chroma index from JSONL...")

    # Recreate collection cleanly
    existing = {c.name for c in chroma_client.list_collections()}
    if "mkdocs" in existing:
        chroma_client.delete_collection("mkdocs")

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

        meta_raw = {
            "source": item.get("source"),  # full page URL (from your generator)
            "title": item.get("title"),
            "section": item.get("section"),
            "timestamp": item.get("timestamp"),
            # optional extras if present in your JSONL:
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

# Memory (global for now)
chat_history: List[Dict[str, str]] = [
    {"role": "system", "content": "You are a helpful assistant that answers questions about the MkDocs documentation files provided in context."}
]

JSONL_PATH = "../data/chunks/docs.dynamic.jsonl"

@app.on_event("startup")
def startup():
    global collection
    chroma_client = chromadb.Client(Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    ))
    embed_fn = LocalEmbeddingFunction()

    if not os.path.exists(CHROMA_DIR) or "mkdocs" not in [c.name for c in chroma_client.list_collections()]:
        build_chroma_from_jsonl(JSONL_PATH, chroma_client, embed_fn)

    collection = chroma_client.get_collection(name="mkdocs", embedding_function=embed_fn)

# === Ask endpoint ===
@app.post("/ask")
async def ask(req: QuestionRequest):
    global chat_history
    context_chunks = retrieve_context(req.question, collection)
    context_text = "\n\n".join(context_chunks)

    prompt = f"""Use the following context to answer the question. If the answer is not in the context, say you don't know.

Context:
{context_text}

Question: {req.question}
"""

    chat_history.append({"role": "user", "content": prompt})

    try:
        print("comes here")
        response = client.chat.completions.create(
            model="gpt-oss:20b",
            messages=chat_history,
            temperature=0
        )
        reply = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": reply})
        return {"response": reply}
    except Exception as e:
        return {"error": str(e)}
