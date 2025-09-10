#!/usr/bin/env python3
"""
Harvest Q&A candidates from Discord threads using AUTHORSHIP-AWARE blocks.

Two input modes:

1) --raw-glob "path/to/*.json"
   Each file is a raw DiscordChatExporter JSON with a "messages" array.
   We will parse per-message author_id, content, timestamp, and build author blocks.

2) --threads-jsonl path/to/threads.jsonl
   Each line is a JSON thread object. Preferred if it includes "messages": [...]
   If only "text" exists (no messages), we fall back to line-based heuristic.

Output:
- eval/gold_candidates_discord_authored.jsonl
- eval/gold_candidates_discord_authored.csv  (if --write-csv)

Example Usage:
uv run python utils/harvest_gold_from_discord_authored.py \
  --threads-jsonl external/discord/stripped/issues.jsonl \
  --out-jsonl eval/gold_candidates_discord_authored.jsonl \
  --write-csv


Heuristics:
- Merge consecutive messages from the same author into a "block".
- Detect question blocks (ends with ?, has interrogatives, troubleshooting cues).
- Build the QUESTION by concatenating the current question block with any
  immediately-previous blocks by the same author (multi-message questions).
- Build the ANSWER as the next block by a different author, plus their subsequent
  consecutive blocks (multi-message answers).
- Score and filter with --min-score.

No external dependencies beyond stdlib.
"""

import argparse, csv, json, re, glob
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# ---- Simple regexes for Q/A scoring ----
Q_WORDS = (
    r"(how|why|what|where|when|which|who|can|could|should|is|are|does|do|anyone|help)"
)
A_HINTS = r"(try|use|run|click|set|install|link|configure|update|check|ensure|pass|call|create|open)"
URL_RE = re.compile(r"https?://\S+")
CODE_RE = re.compile(r"`[^`]+`|```[\s\S]+?```")


# ---------- Scorers ----------
def sent_score_question(text: str) -> float:
    s = (text or "").strip()
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
    n = len(s)
    if n < 12:
        score -= 0.2
    if n > 1200:
        score -= 0.2
    return max(0.0, min(score, 1.0))


def sent_score_answer(text: str) -> float:
    s = (text or "").strip()
    if not s:
        return 0.0
    score = 0.0
    if re.search(rf"\b{A_HINTS}\b", s, re.I):
        score += 0.3
    if URL_RE.search(s):
        score += 0.2
    if CODE_RE.search(s):
        score += 0.2
    if re.search(r"--\w+|/\w+|\\\w+|\b\d+\.\d+(\.\d+)?\b", s):
        score += 0.15
    n = len(s)
    if n < 15:
        score -= 0.2
    if n > 2000:
        score -= 0.2
    return max(0.0, min(score, 1.0))


# ---------- Utilities ----------
def clean_text(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def load_raw_threads_from_glob(pattern: str) -> List[Dict]:
    out = []
    for path in glob.glob(pattern):
        p = Path(path)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        guild = data.get("guild") or {}
        channel = data.get("channel") or {}
        title = channel.get("name") or p.stem
        section = channel.get("category") or (guild.get("name") or "")
        messages = data.get("messages") or []
        # Normalize message records
        msgs = []
        for m in messages:
            t = (m.get("content") or "").strip()
            if not t:
                continue
            author = m.get("author") or {}
            msgs.append(
                {
                    "author_id": author.get("id") or "",
                    "author_name": author.get("nickname") or author.get("name") or "",
                    "timestamp": m.get("timestamp") or "",
                    "content": t,
                }
            )
        if not msgs:
            continue
        # Thread id: file name or channel id + first timestamp
        tid = f"{p.stem}"
        first_ts = msgs[0].get("timestamp", "")
        out.append(
            {
                "id": tid,
                "title": title,
                "section": section,
                "messages": msgs,
                "url": None,
                "timestamp": first_ts,
            }
        )
    return out


def load_threads_jsonl(path: Path) -> List[Dict]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                out.append(rec)
            except Exception:
                pass
    return out


def to_blocks_from_messages(messages: List[Dict]) -> List[Dict]:
    """
    Merge consecutive messages from the same author into 'blocks'.
    Each block: {author_id, author_name, start_idx, end_idx, text}
    """
    blocks = []
    cur = None
    for i, m in enumerate(messages):
        aid = m.get("author_id", "")
        txt = clean_text(m.get("content", ""))
        if not txt:
            continue
        if cur and cur["author_id"] == aid:
            cur["end_idx"] = i
            cur["texts"].append(txt)
        else:
            if cur:
                cur["text"] = " ".join(cur["texts"])
                del cur["texts"]
                blocks.append(cur)
            cur = {
                "author_id": aid,
                "author_name": m.get("author_name", ""),
                "start_idx": i,
                "end_idx": i,
                "texts": [txt],
            }
    if cur:
        cur["text"] = " ".join(cur["texts"])
        del cur["texts"]
        blocks.append(cur)
    return blocks


def to_blocks_from_text(text: str) -> List[Dict]:
    """
    Fallback: no authorship. Treat each non-empty line as its own block.
    """
    lines = [clean_text(l) for l in (text or "").split("\n")]
    lines = [l for l in lines if l]
    blocks = []
    for i, l in enumerate(lines):
        blocks.append(
            {
                "author_id": "",
                "author_name": "",
                "start_idx": i,
                "end_idx": i,
                "text": l,
            }
        )
    return blocks


# ---------- Harvest with authorship ----------
def harvest_thread_authored(thread: Dict, min_score: float, max_q: int) -> List[Dict]:
    msgs = thread.get("messages")
    if msgs:
        blocks = to_blocks_from_messages(msgs)
    else:
        # fallback to line-based (no authorship)
        blocks = to_blocks_from_text(thread.get("text", ""))

    if not blocks:
        return []

    # Detect question blocks
    q_idxs = [(i, sent_score_question(b["text"])) for i, b in enumerate(blocks)]
    q_idxs = [(i, s) for (i, s) in q_idxs if s >= 0.6]

    # Thin out very dense detections (keep stronger if adjacent)
    filtered = []
    last = -999
    for i, s in q_idxs:
        if i - last < 1:
            if filtered and s > filtered[-1][1]:
                filtered[-1] = (i, s)
            continue
        filtered.append((i, s))
        last = i
    q_idxs = filtered[:max_q]

    out = []
    for qi, qscore in q_idxs:
        qb = blocks[qi]
        asker = qb["author_id"]

        # Build QUESTION: include immediately previous blocks by the SAME author
        q_text_parts = [qb["text"]]
        j = qi - 1
        while j >= 0 and blocks[j]["author_id"] == asker:
            # prepend previous same-author block
            q_text_parts.insert(0, blocks[j]["text"])
            j -= 1
        question_text = " ".join(q_text_parts).strip()

        # Build ANSWER: next block by a DIFFERENT author, plus their subsequent consecutive blocks
        ans_start = None
        for k in range(qi + 1, len(blocks)):
            if blocks[k]["author_id"] and blocks[k]["author_id"] != asker:
                ans_start = k
                break
        if ans_start is None:
            continue  # no answer found

        answerer = blocks[ans_start]["author_id"]
        a_text_parts = [blocks[ans_start]["text"]]
        k = ans_start + 1
        while k < len(blocks) and blocks[k]["author_id"] == answerer:
            a_text_parts.append(blocks[k]["text"])
            k += 1
        answer_text = " ".join(a_text_parts).strip()

        if not answer_text:
            continue

        # Score the assembled texts
        a_base = sent_score_answer(answer_text)
        # bonus for links/code in answer
        if URL_RE.search(answer_text):
            a_base += 0.1
        if CODE_RE.search(answer_text):
            a_base += 0.1
        # proximity: fewer blocks between Q and A
        distance = max(1, ans_start - qi)
        prox = max(0.0, 0.2 - 0.05 * (distance - 1))
        final = max(0.0, min(1.0, 0.55 * qscore + 0.35 * a_base + prox))
        if final < min_score:
            continue

        rec = {
            "id": f"{thread.get('id','')}|q{qi}-a{ans_start}",
            "thread_id": thread.get("id", ""),
            "title": thread.get("title", ""),
            "section": thread.get("section", ""),
            "question": question_text,
            "proposed_answer": answer_text,
            "source_url": thread.get("url"),
            "timestamp": thread.get("timestamp", ""),
            "method": "discord_authored_blocks",
            "score": round(final, 2),
            "q_block": qi,
            "a_block": ans_start,
            "asker_id": asker,
            "answerer_id": answerer,
        }
        out.append(rec)

    return out


# ---------- IO ----------
def save_jsonl(recs: List[Dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def save_csv(recs: List[Dict], path: Path):
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
        "thread_id",
        "q_block",
        "a_block",
        "asker_id",
        "answerer_id",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in recs:
            w.writerow({k: r.get(k, "") for k in cols})


# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--raw-glob",
        help="Glob for raw DiscordChatExporter JSON files (e.g., external/discord/raw/*.json)",
    )
    ap.add_argument(
        "--threads-jsonl",
        help="Alternative: JSONL with per-thread objects; prefer ones that include 'messages'",
    )
    ap.add_argument(
        "--out-jsonl", default="eval/gold_candidates_discord_authored.jsonl"
    )
    ap.add_argument("--out-csv", default="eval/gold_candidates_discord_authored.csv")
    ap.add_argument("--min-score", type=float, default=0.62)
    ap.add_argument("--max-q-per-thread", type=int, default=5)
    ap.add_argument("--write-csv", action="store_true")
    args = ap.parse_args()

    threads: List[Dict] = []
    if args.raw_glob:
        threads.extend(load_raw_threads_from_glob(args.raw_glob))
    if args.threads_jsonl:
        threads.extend(load_threads_jsonl(Path(args.threads_jsonl)))

    if not threads:
        raise SystemExit(
            "No threads loaded. Provide --raw-glob and/or --threads-jsonl."
        )

    all_cands: List[Dict] = []
    for th in threads:
        cands = harvest_thread_authored(
            th, min_score=args.min_score, max_q=args.max_q_per_thread
        )
        all_cands.extend(cands)

    # sort best-first
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
