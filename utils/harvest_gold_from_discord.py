#!/usr/bin/env python3
"""
Harvest Q&A candidates from normalized Discord threads (JSONL).

Input JSONL record (one per thread), minimally:
{
  "id": "thread-stable-id",
  "title": "Thread title",
  "section": "Channel/Category",
  "text": "line1\nline2\n…",
  "url": null,
  "timestamp": "2025-03-18T10:11:12Z"
}

Output:
- eval/data/gold_candidates_discord.jsonl
- eval/data/gold_candidates_discord.csv  (if --write-csv)

Heuristics:
- detect Q-lines (question marks + interrogatives + troubleshooting cues)
- choose the next plausible A-span (action verbs, links/code, length bounds)
- score & filter by --min-score

Example Usage:
uv run python utils/harvest_gold_from_discord.py \
  --threads-jsonl external/discord/stripped/issues.jsonl \
  --out-jsonl eval/data/gold_candidates_discord.jsonl \
  --out-csv  eval/data/gold_candidates_discord.csv \
  --write-csv \
  --min-score 0.62 \
  --max-q-per-thread 50


No external deps beyond stdlib.
"""

import argparse, csv, hashlib, json, re
from pathlib import Path
from typing import List, Tuple, Optional

Q_WORDS = (
    r"(how|why|what|where|when|which|who|can|could|should|is|are|does|do|anyone|help)"
)
A_HINTS = r"(try|use|run|click|set|install|link|configure|update|check|ensure|pass|call|create|open)"
URL_RE = re.compile(r"https?://\S+")
CODE_RE = re.compile(r"`[^`]+`|```[\s\S]+?```")


def sent_score_question(line: str) -> float:
    s = line.strip()
    if not s:
        return 0.0
    score = 0.0
    if s.endswith("?"):
        score += 0.5
    if re.search(rf"^\s*{Q_WORDS}\b", s, re.I):
        score += 0.35
    if re.search(rf"\b{Q_WORDS}\b", s, re.I):
        score += 0.15
    if re.search(r"\b(error|fail|traceback|exception|bug)\b", s, re.I):
        score += 0.1
    # Penalize very long or very short
    n = len(s)
    if n < 12:
        score -= 0.2
    if n > 600:
        score -= 0.2
    return max(0.0, min(score, 1.0))


def sent_score_answer(line: str) -> float:
    s = line.strip()
    if not s:
        return 0.0
    score = 0.0
    if re.search(rf"\b{A_HINTS}\b", s, re.I):
        score += 0.3
    if URL_RE.search(s):
        score += 0.2
    if CODE_RE.search(s):
        score += 0.2
    # Specificity: flags, paths, versions
    if re.search(r"--\w+|/\w+|\\\w+|\b\d+\.\d+(\.\d+)?\b", s):
        score += 0.15
    # Penalize very short/very long
    n = len(s)
    if n < 15:
        score -= 0.2
    if n > 1000:
        score -= 0.2
    return max(0.0, min(score, 1.0))


def choose_answer_span(
    lines: List[str], start_idx: int, max_span: int = 6
) -> Tuple[int, int, float]:
    """
    From the line after start_idx, find a plausible answer span.
    Returns (a_start, a_end_exclusive, span_score) or (-1, -1, 0.0)
    """
    best = (-1, -1, 0.0)
    a_start = start_idx + 1
    if a_start >= len(lines):
        return best

    # Scan until end, or stop early at next question-like line (within 12 lines)
    scan_limit = min(len(lines), a_start + 12)
    next_q = next(
        (k for k in range(a_start, scan_limit) if sent_score_question(lines[k]) >= 0.6),
        None,
    )
    a_stop = next_q if next_q is not None else len(lines)

    # Evaluate spans up to max_span lines
    for s in range(a_start, a_stop):
        for e in range(s + 1, min(a_stop, s + max_span) + 1):
            chunk = " ".join(l.strip() for l in lines[s:e]).strip()
            if not chunk:
                continue
            chunk = re.sub(r"\s+", " ", chunk)
            sent_scores = [sent_score_answer(l) for l in lines[s:e]]
            base = sum(sent_scores) / max(1, len(sent_scores))
            if URL_RE.search(chunk):
                base += 0.1
            if CODE_RE.search(chunk):
                base += 0.1
            n = len(chunk)
            if n < 40:
                base -= 0.1
            if n > 1500:
                base -= 0.2
            base = max(0.0, min(base, 1.0))
            if base > best[2]:
                best = (s, e, base)
    return best


def thread_candidates(
    thread: dict, min_score: float, max_q_per_thread: int
) -> List[dict]:
    text = (thread.get("text") or "").strip()
    if not text:
        return []
    # split to rough "lines" (Discord-like)
    raw_lines = [l.strip() for l in text.split("\n")]
    lines = [l for l in raw_lines if l]  # drop empties

    # find question lines
    q_idxs = [(i, sent_score_question(lines[i])) for i in range(len(lines))]
    q_idxs = [(i, s) for (i, s) in q_idxs if s >= 0.6]
    # limit density: skip near-duplicates (very close indices)
    filtered = []
    last = -999
    for i, s in q_idxs:
        if i - last < 2:
            # keep the stronger one
            if filtered and s > filtered[-1][1]:
                filtered[-1] = (i, s)
            continue
        filtered.append((i, s))
        last = i
    q_idxs = filtered[:max_q_per_thread]

    out = []
    for i, q_score in q_idxs:
        a_s, a_e, a_score = choose_answer_span(lines, i)
        if a_s == -1:
            continue
        q = lines[i]
        a = " ".join(lines[a_s:a_e]).strip()
        # final score mix
        # nearer answer gets slight boost
        distance = max(1, a_s - i)
        prox = max(0.0, 0.2 - 0.02 * (distance - 1))
        final = max(0.0, min(1.0, 0.55 * q_score + 0.35 * a_score + prox))

        if final < min_score:
            continue

        rec = {
            "id": f"{thread.get('id','')}|q{i}-a{a_s}-{a_e}",
            "thread_id": thread.get("id", ""),
            "title": thread.get("title", ""),
            "section": thread.get("section", ""),
            "question": q,
            "proposed_answer": a,
            "source_url": thread.get("url"),
            "timestamp": thread.get("timestamp", ""),
            "method": "discord_thread_heuristic",
            "score": round(final, 2),
            "q_line": i,
            "a_start": a_s,
            "a_end": a_e,
        }
        out.append(rec)
    return out


def load_threads_jsonl(path: Path) -> List[dict]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def save_jsonl(recs: List[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def save_csv(recs: List[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "id",
        "score",
        "method",
        "title",
        "section",
        "question",
        "proposed_answer",
        "source_url",
        "timestamp",
        "q_line",
        "a_start",
        "a_end",
        "thread_id",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in recs:
            w.writerow({k: r.get(k, "") for k in cols})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--threads-jsonl", required=True, help="Path to normalized threads JSONL"
    )
    ap.add_argument("--out-jsonl", default="eval/data/gold_candidates_discord.jsonl")
    ap.add_argument("--out-csv", default="eval/data/gold_candidates_discord.csv")
    ap.add_argument("--min-score", type=float, default=0.6)
    ap.add_argument(
        "--max-q-per-thread", type=int, default=3, help="Max Qs to propose per thread"
    )
    ap.add_argument("--write-csv", action="store_true")
    args = ap.parse_args()

    threads = load_threads_jsonl(Path(args.threads_jsonl))
    all_cands = []
    for th in threads:
        cands = thread_candidates(
            th, min_score=args.min_score, max_q_per_thread=args.max_q_per_thread
        )
        all_cands.extend(cands)

    # deterministic order: by score desc then timestamp
    all_cands.sort(key=lambda r: (r["score"], r.get("timestamp", "")), reverse=True)

    save_jsonl(all_cands, Path(args.out_jsonl))
    if args.write_csv:
        save_csv(all_cands, Path(args.out_csv))

    print(f"✅ Wrote {len(all_cands)} candidates")
    print(f"JSONL: {args.out_jsonl}")
    if args.write_csv:
        print(f"CSV:   {args.out_csv}")


if __name__ == "__main__":
    main()
