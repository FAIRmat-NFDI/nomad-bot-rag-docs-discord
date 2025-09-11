import argparse, json, os, uuid, subprocess, datetime
from typing import Dict, Any, List, Optional
from tqdm import tqdm
import pandas as pd

from .text_metrics import token_f1, exact_match, jaccard, levenshtein_ratio
from .semantics import semantic_sim
from .model_adapter import generate_answer
from .judges import judge_openai

def load_jsonl(path: str) -> List[Dict[str, Any]]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "id" not in obj:
                obj["id"] = str(uuid.uuid4())
            items.append(obj)
    return items

def _git_sha() -> Optional[str]:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None

def evaluate(items: List[Dict[str, Any]], use_llm_judge: bool = False, judge_cache: Optional[str] = None) -> pd.DataFrame:
    rows = []
    for obj in tqdm(items, desc="Evaluating"):
        q = obj.get("question", "")
        gold = obj.get("answer", "")
        source = obj.get("source", "unknown")
        _id = obj.get("id")
        pred = generate_answer(q, meta={"source": source, "id": _id})
        row = {
            "id": _id,
            "source": source,
            "question": q,
            "gold_answer": gold,
            "model_answer": pred,
            "em": exact_match(pred, gold),
            "f1": token_f1(pred, gold),
            "jaccard": jaccard(pred, gold),
            "lev_ratio": levenshtein_ratio(pred, gold),
        }
        sem = semantic_sim(pred, gold)
        row["semantic_sim"] = sem if sem is not None else None
        rows.append(row)
    df = pd.DataFrame(rows)
    if use_llm_judge:
        batch = [{"id": r.id, "question": r.question, "gold": r.gold_answer, "pred": r.model_answer} for r in df.itertuples()]
        try:
            judged = judge_openai(batch, cache_path=judge_cache)
            jdf = pd.DataFrame(judged)
            df = df.merge(jdf, on="id", how="left")
        except Exception as e:
            print(f"[WARN] LLM judge failed: {e}")
            df["judge_score"] = None
            df["judge_rationale"] = None
    return df

def _write_metadata(out_dir: str, args: argparse.Namespace, n_items: int):
    meta = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "git_sha": _git_sha(),
        "data_path": args.data_path,
        "use_llm_judge": bool(args.use_llm_judge),
        "judge_cache": args.judge_cache,
        "notes": args.notes,
        "n_items": n_items,
        "config": {"semantic_model": "all-MiniLM-L6-v2"}
    }
    with open(os.path.join(out_dir, "config_snapshot.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_path", required=True, help="Path to gold_all.jsonl")
    ap.add_argument("--out_dir", default="runs/eval", help="Where to write outputs")
    ap.add_argument("--use_llm_judge", action="store_true")
    ap.add_argument("--judge_cache", default="runs/judge_cache.parquet", help="Cache file for judge results")
    ap.add_argument("--notes", default="", help="Optional note for this run")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    items = load_jsonl(args.data_path)
    df = evaluate(items, use_llm_judge=args.use_llm_judge, judge_cache=args.judge_cache)
    out_parquet = os.path.join(args.out_dir, "eval_results.parquet")
    out_csv = os.path.join(args.out_dir, "eval_results.csv")
    df.to_parquet(out_parquet, index=False)
    df.to_csv(out_csv, index=False)
    _write_metadata(args.out_dir, args, n_items=len(items))
    print(f"Wrote: {out_parquet}\nWrote: {out_csv}\nMeta: {os.path.join(args.out_dir, 'config_snapshot.json')}")

if __name__ == "__main__":
    main()
