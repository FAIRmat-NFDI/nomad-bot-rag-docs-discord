# nomad-bot-rag-docs-discord
A prototype chatbot built with retrieval-augmented generation (RAG) to assist researchers and developers working with the NOMAD platform.

## Quick Start

1. **Install dependencies**: Download `uv` [here](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) to install and manage packages (recommended). Change the folder `my_project` to the name of your project, and modify the `pyproject.toml` file to include the name and a short description of your project. Then, install the package and its dependencies:

   ```bash
   uv sync
   uv pip install -e .
   ```

   (Alternative: create a conda environment and run `pip install -e .`)

2. **Add your API key**:

   ```bash
   cp .env.example .env
   # Edit .env with your API key
   ```

3. **Run the app**:

   ```bash
   uv run main.py
   ```

   (Alternative: run with `python main.py`)

4. **Open your browser** to `http://localhost:7860` to use the web interface!

5. **Customize!** Modify the Gradio app, package structure, and add your own features! Make sure to add a "graphical abstract" of your work as well.

## Adding New Features

```bash
# Add a new package
uv add package-name
```

## Project Structure

```
├── main.py              # Your main application with Gradio
├── notebooks/           # Notebooks for prototyping
├── src/
│   └── my_project/      # Your code goes here
├── .env.example         # Template for API keys
└── pyproject.toml       # Dependencies
```

## Using the evaluation dashboard

pip install -e ".[eval]"

# Evaluate
ragbot-eval --data_path data/gold_all.jsonl --out_dir runs/2025-09-11 --use_llm_judge

# Dashboard
ragbot-eval-dash --results_path runs/2025-09-11/eval_results.parquet

