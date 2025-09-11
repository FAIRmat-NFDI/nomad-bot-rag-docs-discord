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

        collection.add(
            documents=[text],
            metadatas=[{
                "source": item.get("source"),
                "title": item.get("title"),
                "section": item.get("section"),
                "url": item.get("url"),
                "timestamp": item.get("timestamp"),
            }],
            ids=[item.get("id", f"chunk_{count}")]
        )
        print("working")
        count += 1

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

JSONL_PATH = "../data/docs/nomad_docs.dynamic.jsonl"

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
