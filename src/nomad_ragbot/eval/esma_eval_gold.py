# scripts/eval_gold.py
# Run:
#uv run -- python scripts/esma_eval_gold.py \
#  --gold eval/data/gold_all.jsonl \
#  --out  eval/data/run_gold_all \
#  --semantic \
#  --embed-url http://172.28.105.142:11434/api/embed \
#  --embed-model nomic-embed-text

import argparse, json, time, os, csv, math
from pathlib import Path
import requests
from difflib import SequenceMatcher
from collections import Counter

# ---------- IO ----------

def read_jsonl(p: Path):
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

def write_jsonl(rows, p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def write_csv(rows, p: Path, fieldnames):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})

# ---------- Text utils & metrics ----------

def norm_text(s: str) -> str:
    return " ".join((s or "").lower().strip().split())

def tokens(s: str):
    return [t for t in norm_text(s).split() if t]

def f1_score(pred: str, gold: str) -> float:
    p_toks, g_toks = tokens(pred), tokens(gold)
    if not p_toks and not g_toks:
        return 1.0
    if not p_toks or not g_toks:
        return 0.0
    pc, gc = Counter(p_toks), Counter(g_toks)
    common = sum((pc & gc).values())
    if common == 0:
        return 0.0
    precision = common / max(1, len(p_toks))
    recall    = common / max(1, len(g_toks))
    return 2 * precision * recall / max(precision + recall, 1e-12)

def exact_match(pred: str, gold: str) -> int:
    return int(norm_text(pred) == norm_text(gold))

def sim_ratio(pred: str, gold: str) -> float:
    return SequenceMatcher(None, norm_text(pred), norm_text(gold)).ratio()

# ---------- Semantic similarity (optional) ----------

def embed(text: str, base_url="http://127.0.0.1:11434/api/embed", model="nomic-embed-text", timeout=20):
    if not text or not text.strip():
        return None
    r = requests.post(base_url, json={"model": model, "input": text}, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if "embeddings" in data and data["embeddings"]:
        return data["embeddings"][0]
    if "embedding" in data:
        return data["embedding"]
    return None

def cosine(u, v):
    if not u or not v:
        return None
    num = sum(a*b for a, b in zip(u, v))
    du = math.sqrt(sum(a*a for a in u))
    dv = math.sqrt(sum(b*b for b in v))
    if du == 0 or dv == 0:
        return None
    return num / (du * dv)

# ---------- Field detection ----------

def detect_fields(sample: dict):
    """
    Infer question and gold from heterogeneous records.
    Supported question keys: question | query | prompt
    Supported gold keys: gold | answer | reference | expected | target | gold_answer
    """
    q = (sample.get("question")
         or sample.get("query")
         or sample.get("prompt"))

    g = (sample.get("gold")
         or sample.get("answer")
         or sample.get("reference")
         or sample.get("expected")
         or sample.get("target")
         or sample.get("gold_answer"))  # important for your mixed file

    # Treat empty strings as missing
    if g is not None and str(g).strip() == "":
        g = None

    return q, g

# ---------- Main ----------

def main():
    ap = argparse.ArgumentParser(description="Evaluate /ask against a gold JSONL.")
    ap.add_argument("--gold", required=True, help="Path to gold JSONL (e.g., data/gold_all.jsonl)")
    ap.add_argument("--api", default=os.getenv("API_BASE_URL", "http://127.0.0.1:8000"),
                    help="Base URL of FastAPI server (default http://127.0.0.1:8000)")
    ap.add_argument("--endpoint", default="/ask", help="Ask endpoint path (default /ask)")
    ap.add_argument("--out", default="eval/data/run_gold_all",
                    help="Output prefix (we write <out>.jsonl, <out>.csv, <out>.scores.csv)")
    ap.add_argument("--sleep", type=float, default=0.1, help="Sleep between requests (sec)")
    ap.add_argument("--timeout", type=float, default=60, help="HTTP timeout (sec)")
    ap.add_argument("--limit", type=int, default=0, help="Evaluate only first N (0 = all)")
    ap.add_argument("--semantic", action="store_true",
                    help="Also compute semantic cosine similarity via local embedding endpoint.")
    ap.add_argument("--embed-url", default="http://127.0.0.1:11434/api/embed",
                    help="Embedding endpoint (OpenAI-compatible /api/embed)")
    ap.add_argument("--embed-model", default="nomic-embed-text", help="Embedding model name")
    args = ap.parse_args()

    gold_path = Path(args.gold).resolve()
    api_url = args.api.rstrip("/") + args.endpoint
    out_prefix = Path(args.out)
    out_jsonl = out_prefix.with_suffix(".jsonl")
    out_csv   = out_prefix.with_suffix(".csv")
    scores_csv = out_prefix.with_suffix(".scores.csv")
    missing_path = out_prefix.with_suffix(".missing_gold.jsonl")

    print(f"→ Reading gold from: {gold_path}")
    print(f"→ Posting to: {api_url}")
    print(f"→ Writing: {out_jsonl}, {out_csv}")

    rows = []
    missing = []

    # aggregation (only over rows that have a gold)
    s_em = s_f1 = s_sim = s_sem = 0.0
    n = 0  # count of rows with gold
    total_rows = 0
    processed = 0

    for i, row in enumerate(read_jsonl(gold_path), 1):
        total_rows += 1
        q, g = detect_fields(row)
        if not q:
            continue
        if args.limit and processed >= args.limit:
            break

        try:
            r = requests.post(api_url, json={"question": q}, timeout=args.timeout)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                pred = ""
                citations = ""
                err = data["error"]
            else:
                pred = data.get("answer", "") or data.get("response", "")
                citations = data.get("citations", "")
                err = None
        except Exception as e:
            pred, citations, err = "", "", str(e)

        # Metrics
        em = f1 = sim = sem = None
        if g is None:
            missing.append({"idx": i, "question": q})
        else:
            em  = exact_match(pred, g)
            f1  = f1_score(pred, g)
            sim = sim_ratio(pred, g)

            if args.semantic:
                try:
                    eg = embed(g, base_url=args.embed_url, model=args.embed_model)
                    ep = embed(pred, base_url=args.embed_url, model=args.embed_model)
                    sem = cosine(eg, ep) if (eg and ep) else None
                except Exception:
                    sem = None

            s_em  += em
            s_f1  += f1
            s_sim += sim
            if sem is not None:
                s_sem += sem
            n += 1

        result = {
            "idx": i,
            "question": q,
            "gold": g,
            "pred": pred,
            "citations": citations,
            "error": err,
            "em": em,
            "f1": f1,
            "sim": sim,
            "sem": sem,  # may be None if --semantic not used
        }
        rows.append(result)
        processed += 1

        if i % 10 == 0:
            print(f"...{i} processed")
        time.sleep(args.sleep)

    # Save results
    write_jsonl(rows, out_jsonl)
    write_csv(
        rows,
        out_csv,
        fieldnames=["idx", "question", "gold", "pred", "em", "f1", "sim", "sem", "citations", "error"]
    )

    # Scores-only CSV
    score_fields = ["idx", "question", "em", "f1", "sim", "sem", "error"]
    write_csv(
        [{k: r.get(k) for k in score_fields} for r in rows],
        scores_csv,
        fieldnames=score_fields
    )
    print(f"→ Scores CSV: {scores_csv}")

    # Missing-gold list
    if missing:
        write_jsonl(missing, missing_path)
        print(f"→ Wrote missing-gold list: {missing_path}")

    # Summary
    if n > 0:
        avg_em  = s_em / n
        avg_f1  = s_f1 / n
        avg_sim = s_sim / n
        line = [
            f"\n== Summary on {n} rows WITH gold ==",
            f"Exact Match:      {avg_em:.3f}",
            f"F1:               {avg_f1:.3f}",
            f"Char similarity:  {avg_sim:.3f}",
        ]
        if args.semantic:
            avg_sem = s_sem / n
            line.append(f"Semantic cosine:  {avg_sem:.3f}")
        print("\n".join(line))
    else:
        print("\nNo gold answers found; saved raw predictions only.")

    coverage = (n / total_rows * 100.0) if total_rows else 0.0
    print(f"Gold coverage: {n}/{total_rows} rows ({coverage:.1f}%)")

if __name__ == "__main__":
    main()
