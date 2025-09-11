# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai",
#     "bs4",
#     "chromadb",
#     "tiktoken",
#     "markdown",
# ]
# ///
import os
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from markdown import markdown
from bs4 import BeautifulSoup
import requests

# ==== CONFIG ====
DOCS_DIR = "./docs"
CHROMA_DIR = "./chroma_store"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ==== LOAD & CHUNK DOCS ====
import requests

class LocalEmbeddingFunction:
    def __init__(self, model_name=EMBED_MODEL):
        self.model_name = model_name  # ✅ Set this before using it

    def __call__(self, input: list[str]) -> list[list[float]]:
        embeddings = []
        for text in input:
            response = requests.post(
                "http://172.28.105.142:11434/api/embed",  # Or adjust path as needed
                json={
                    "model": self.model_name,  # Or your actual local embedding model
                    "input": text
                }
            )
            data = response.json()
            embeddings.append(data['embeddings'][0])
        return embeddings
    def name(self) -> str:
        # ✅ This is required by ChromaDB to track config
        return f"{self.model_name}"

def read_markdown_files(directory):
    docs = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".md"):
                path = os.path.join(root, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    docs.append((path, content))
    return docs

def markdown_to_text(md_content):
    html = markdown(md_content)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    tokens = text.split()
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i+chunk_size]
        chunks.append(" ".join(chunk))
    return chunks

def build_chroma_index(docs):
    print("🔧 Building Chroma index...")
    chroma_client = chromadb.Client(Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    ))

    embed_fn = LocalEmbeddingFunction()

    if "mkdocs" in [c.name for c in chroma_client.list_collections()]:
        chroma_client.delete_collection("mkdocs")

    collection = chroma_client.create_collection(name="mkdocs", embedding_function=embed_fn)

    doc_id = 0
    for path, md in docs:
        text = markdown_to_text(md)
        chunks = chunk_text(text)
        for chunk in chunks:
            collection.add(
                documents=[chunk],
                metadatas=[{"source": path}],
                ids=[f"doc_{doc_id}"]
            )
            doc_id += 1

    print("✅ Indexing complete.")
    return collection

# ==== RETRIEVAL + OPENAI CHAT ====

client = OpenAI(
    base_url="http://172.28.105.142:11434/v1",  # note: use /v1, not /api
    api_key="not-needed"  # can be anything if your server doesn't validate it
)
def retrieve_context(query, collection, top_k=3):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results['documents'][0] if results['documents'] else []

def chat_loop(collection):
    print("🤖 Ask me anything about your MkDocs docs! Type 'exit' to quit.\n")
    
    messages = [{"role": "system", "content": "You are a helpful assistant that answers questions about the MkDocs documentation files provided in context."}]

    while True:
        user_input = input("💬 You: ")
        if user_input.strip().lower() in ['exit', 'quit']:
            print("👋 Exiting chat.")
            break

        context_chunks = retrieve_context(user_input, collection)
        context_text = "\n\n".join(context_chunks)

        prompt = f"""Use the following context to answer the question. If the answer is not in the context, say you don't know.

Context:
{context_text}

Question: {user_input}
"""

        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model="gpt-oss:20b",
                messages=messages,
                temperature=0
            )
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

        reply = response.choices[0].message.content
        print(f"\n🤖 {reply}\n")

        messages.append({"role": "assistant", "content": reply})

# ==== MAIN ====

def main():
    chroma_client = chromadb.Client(Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    ))

    embed_fn = LocalEmbeddingFunction()

    if not os.path.exists(CHROMA_DIR) or "mkdocs" not in [c.name for c in chroma_client.list_collections()]:
        docs = read_markdown_files(DOCS_DIR)
        build_chroma_index(docs)

    collection = chroma_client.get_collection(name="mkdocs", embedding_function=embed_fn)
    chat_loop(collection)

if __name__ == "__main__":
    main()
