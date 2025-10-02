# NOMAD RAG Assistant

This project is a sophisticated chatbot built with Retrieval-Augmented Generation (RAG) to assist researchers and developers working with the [NOMAD platform](https://nomad-lab.eu/). It can answer questions about documentation, features, and best practices by retrieving relevant information from a knowledge base and generating concise, accurate answers.

The project features a standalone FastAPI backend for the RAG pipeline, a Gradio web interface for user interaction, and a complete evaluation suite.

---
## Project Structure 📂

This project follows a standard `src` layout to separate source code from project configuration and data. The core logic is located within the `src/nomad_ragbot` package.

```
nomad-bot-rag-docs-discord/
├── .env                  # Local environment variables (ignored by Git)
├── .env.example          # Template for environment variables
├── pyproject.toml        # Project metadata and dependencies
├── uv.lock               # Pinned versions for reproducible builds
├── data/                 # Holds the input data for the knowledge base
├── chroma_store/         # Local vector database storage (ignored by Git)
└── src/
    └── nomad_ragbot/
        ├── api/          # FastAPI Backend
        │   ├── main.py
        │   ├── config.py
        │   └── ...
        │
        ├── query/        # Core RAG logic and query engine
        │   └── query.py
        │
        ├── gradio_app.py # Standalone Gradio Web UI
        ├── llm_client.py # Client for interacting with the LLM
        └── eval/         # Evaluation scripts and dashboard logic
```

* **`src/nomad_ragbot/api/`**: A self-contained FastAPI application that serves the RAG pipeline. It handles indexing the data into a ChromaDB vector store and exposing an `/ask` endpoint.
* **`src/nomad_ragbot/query/`**: The heart of the RAG system. It contains the `RAGQueryEngine` which manages retrieving context, reranking results, and generating answers.
* **`src/nomad_ragbot/gradio_app.py`**: A standalone Gradio web interface for easy interaction with the chatbot. It calls the RAG logic directly.
* **`data/`**: Your source documents (e.g., `docs.dynamic.jsonl`) that will be indexed into the vector database.
* **`chroma_store/`**: The directory where the Chroma vector database is persisted locally. This is automatically generated.

---
## Setup and Installation ⚙️

Follow these steps to set up your local environment. This project uses [`uv`](https://github.com/astral-sh/uv) for fast package and environment management.

### **1. Clone and Set Up the Environment**
First, clone the repository to your local machine.
```bash
git clone [https://github.com/FAIRmat-NFDI/nomad-bot-rag-docs-discord.git](https://github.com/FAIRmat-NFDI/nomad-bot-rag-docs-discord.git)
cd nomad-bot-rag-docs-discord
```
Next, create a virtual environment and install all necessary dependencies using `uv`.
```bash
# Create a virtual environment named .venv
uv venv

# Activate the environment (on macOS/Linux)
source .venv/bin/activate

# Install all packages from pyproject.toml
uv sync
```

### **2. Configure Environment Variables**
Copy the example environment file and edit it with your local settings.
```bash
cp .env.example .env
```
Now, open the `.env` file and configure the paths and model endpoints. The defaults should work for a local setup.
```env
# .env file

# --- Paths ---
JSONL_PATH="data/chunks/docs.dynamic.jsonl"
CHROMA_DIR="chroma_store"

# --- Model Endpoints ---
EMBED_BASE_URL="[http://127.0.0.1:11434](http://127.0.0.1:11434)"
GENERATOR_BASE_URL="[http://127.0.0.1:11434/v1](http://127.0.0.1:11434/v1)"

# You can also customize the models used by the RAG engine here
# EMBED_MODEL_NAME="nomic-embed-text"
# GENERATOR_MODEL="gpt-oss:20b"
```

---
## Running the Application ▶️

The API server and the Gradio UI are two separate applications. You must run them in **two separate terminals**.

### **Terminal 1: Start the API Server**
This server handles the RAG logic and indexing. The first time you run it, it will build the ChromaDB vector store, which may take a few minutes.

```bash
uvicorn src.nomad_ragbot.api.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### **Terminal 2: Start the Gradio Web UI**
This command launches the user-friendly web interface for asking questions.

```bash
uv run python -m src.nomad_ragbot.gradio_app
```
You can now open your browser and navigate to **`http://127.0.0.1:7860`** to interact with the chatbot!

---
## Evaluation Dashboard 📊

The project includes a suite for evaluating the performance of the RAG pipeline.

### **1. Install Evaluation Dependencies**
Install the project in editable mode with the optional `[eval]` dependencies.
```bash
pip install -e ".[eval]"
```

### **2. Run Evaluation**
Execute the evaluation script against a "golden dataset" of questions and answers.
```bash
ragbot-eval --data_path data/evaluation/gold_all.jsonl --out_dir runs/your-run-name --use_llm_judge
```

### **3. View the Dashboard**
Launch the evaluation dashboard to visualize the results from your run.
```bash
ragbot-eval-dash --results_path runs/your-run-name/eval_results.parquet
```