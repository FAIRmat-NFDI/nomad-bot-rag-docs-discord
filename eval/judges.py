from typing import List, Dict, Any, Optional
import json, re, os, hashlib
import pandas as pd

JUDGE_PROMPT = (
    "You are an expert evaluator. Compare the MODEL_ANSWER to the GOLD_ANSWER for the QUESTION.\n"
    "Score correctness from 0 to 1 (1 = fully correct, 0 = incorrect). Return ONLY JSON like:\n"
    "{\"score\": 0.0-1.0, \"rationale\": \"<short reason>\"}.\n\n"
    "QUESTION: {question}\n"
    "GOLD_ANSWER: {gold}\n"
    "MODEL_ANSWER: {pred}\n"
)

def _make_key(item: Dict[str, Any]) -> str:
    m = hashlib.sha256()
    m.update((item.get("id","") + "||" + item.get("question","") + "||" + item.get("pred","")).encode("utf-8"))
    return m.hexdigest()[:16]

def _load_cache(path: Optional[str]) -> Dict[str, Dict[str, Any]]:
    if not path or not os.path.exists(path):
        return {}
    try:
        df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
        return {str(r["cache_key"]): {"judge_score": r["judge_score"], "judge_rationale": r["judge_rationale"]} for _, r in df.iterrows()}
    except Exception:
        return {}

def _save_cache(path: str, rows: List[Dict[str, Any]]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(rows)
    if path.endswith(".parquet"):
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False)

def judge_openai(batch: List[Dict[str, Any]], client=None, model: str = "gpt-4o-mini", cache_path: Optional[str] = None) -> List[Dict[str, Any]]:
    cache = _load_cache(cache_path)
    to_run, out = [], []
    for item in batch:
        key = _make_key(item)
        if key in cache:
            out.append({"id": item["id"], **cache[key]})
        else:
            item["_cache_key"] = key
            to_run.append(item)

    if to_run:
        if client is None:
            try:
                from openai import OpenAI
                client = OpenAI()
            except Exception as e:
                raise RuntimeError("OpenAI client not available. Install `openai` and set OPENAI_API_KEY.") from e

        new_cache_rows = []
        for item in to_run:
            prompt = JUDGE_PROMPT.format(question=item["question"], gold=item["gold"], pred=item["pred"])
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            text = resp.choices[0].message.content.strip()
            match = re.search(r"\{.*\}", text, re.S)
            if match:
                try:
                    obj = json.loads(match.group(0))
                    score = float(obj.get("score", 0.0))
                    rationale = str(obj.get("rationale", ""))
                except Exception:
                    score, rationale = 0.0, f"Unparseable JSON: {text[:200]}"
            else:
                score, rationale = 0.0, f"No JSON found: {text[:200]}"
            row = {"id": item["id"], "judge_score": score, "judge_rationale": rationale}
            out.append(row)
            new_cache_rows.append({"cache_key": item["_cache_key"], **row})

        if cache_path:
            prev = []
            if os.path.exists(cache_path):
                try:
                    prev_df = pd.read_parquet(cache_path) if cache_path.endswith(".parquet") else pd.read_csv(cache_path)
                    prev = prev_df.to_dict("records")
                except Exception:
                    prev = []
            merged = {r["cache_key"]: r for r in prev}
            for r in new_cache_rows:
                merged[r["cache_key"]] = r
            _save_cache(cache_path, list(merged.values()))

    return out
