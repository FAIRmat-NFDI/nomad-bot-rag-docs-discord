# make sure you're in your project root (where pyproject.toml lives)
uv run ragbot-eval \
  --data_path data/gold_all.jsonl \
  --out_dir runs/2025-09-11 \
  --use_llm_judge

