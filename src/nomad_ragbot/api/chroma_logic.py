# src/api/chroma_logic.py
import os
import json
from hashlib import sha256
from datetime import datetime
from typing import Set
import chromadb

from .embeddings import LocalEmbeddingFunction
from . import config

# Manifest file lives inside the ChromaDB directory
MANIFEST_NAME = f"{config.COLLECTION_NAME}.manifest.json"

# ==== Helper Functions ====
def _load_jsonl_chunks(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line := line.strip():
                yield json.loads(line)

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

def _make_unique_id(rid: str, item: dict, seen: Set[str], counter: int) -> str:
    if rid not in seen:
        return rid
    path = item.get("path") or item.get("path_normalized") or item.get("path_original") or ""
    src = item.get("source") or ""
    sec = item.get("section") or ""
    base = f"{rid}|{path}|{src}|{sec}"
    suffix = abs(hash(base)) % (10**8)
    cand = f"{rid}::{suffix}"
    while cand in seen:
        counter += 1
        cand = f"{rid}::{suffix}-{counter}"
    return cand

# ==== Manifest Management ====
def _load_manifest(chroma_dir: str) -> dict:
    mpath = os.path.join(chroma_dir, MANIFEST_NAME)
    if not os.path.exists(mpath):
        return {}
    try:
        with open(mpath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def _save_manifest(chroma_dir: str, manifest: dict) -> None:
    os.makedirs(chroma_dir, exist_ok=True)
    mpath = os.path.join(chroma_dir, MANIFEST_NAME)
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

def _current_signature() -> dict:
    h = sha256()
    with open(config.JSONL_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    jsonl_sha256 = h.hexdigest()

    return {
        "jsonl_path": os.path.abspath(config.JSONL_PATH),
        "jsonl_sha256": jsonl_sha256,
        "embedding_model": config.EMBED_MODEL_NAME,
        "embedding_base_url": config.EMBED_BASE_URL.rstrip("/"),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "collection_name": config.COLLECTION_NAME,
    }

# ==== Core Indexing Logic ====
def _build_collection_from_jsonl(chroma_client, embed_fn):
    print(f"🔧 Rebuilding Chroma collection '{config.COLLECTION_NAME}'...")
    if collection_exists(chroma_client, config.COLLECTION_NAME):
        chroma_client.delete_collection(config.COLLECTION_NAME)

    collection = chroma_client.create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embed_fn
    )

    ids, documents, metadatas = [], [], []
    seen_ids: Set[str] = set()
    count = 0

    for item in _load_jsonl_chunks(config.JSONL_PATH):
        if not (text := item.get("text")) or not str(text).strip():
            continue

        raw_id = str(item.get("id") or f"chunk_{count}")
        rid = _make_unique_id(raw_id, item, seen_ids, count)
        seen_ids.add(rid)

        meta = _sanitize_metadata({
            "source": item.get("source"),
            "title": item.get("title"),
            "section": item.get("section"),
            "timestamp": item.get("timestamp"),
            "repo": item.get("repo"),
            "path": item.get("path") or item.get("path_normalized") or item.get("path_original"),
        })

        ids.append(rid)
        documents.append(str(text))
        metadatas.append(meta)
        count += 1

    if not ids:
        raise RuntimeError(f"No valid records found in {config.JSONL_PATH}")

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"✅ Indexed {count} chunks from JSONL.")
    return collection

def collection_exists(chroma_client, name: str) -> bool:
    try:
        collections = chroma_client.list_collections()
        return any(c.name == name for c in collections)
    except Exception: # Fallback for older chromadb versions
        collections = chroma_client.list_collections()
        return any(c["name"] == name for c in collections)


def ensure_index_up_to_date():
    """
    Checks if the persisted ChromaDB collection is up-to-date. If not, it
    rebuilds it. Returns the ready-to-use collection.
    """
    chroma_client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    embed_fn = LocalEmbeddingFunction()
    
    manifest = _load_manifest(config.CHROMA_DIR)
    want_signature = _current_signature()

    up_to_date = (
        manifest.get("jsonl_sha256") == want_signature["jsonl_sha256"] and
        manifest.get("embedding_model") == want_signature["embedding_model"] and
        manifest.get("embedding_base_url") == want_signature["embedding_base_url"]
    )

    if collection_exists(chroma_client, config.COLLECTION_NAME) and up_to_date:
        print("✅ Index is up-to-date. Reusing existing collection.")
        return chroma_client.get_collection(name=config.COLLECTION_NAME, embedding_function=embed_fn)

    print("⚠️ Index is missing or outdated. Rebuilding...")
    collection = _build_collection_from_jsonl(chroma_client, embed_fn)
    _save_manifest(config.CHROMA_DIR, want_signature)
    return collection
