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
- eval/data/gold_candidates_discord_authored.jsonl
- eval/data/gold_candidates_discord_authored.csv  (if --write-csv)

Example Usage:
uv run python utils/harvest_gold_from_discord_authored.py \
  --threads-jsonl external/discord/stripped/issues.jsonl \
  --out-jsonl eval/data/gold_candidates_discord_authored.jsonl \
  --out-csv  eval/data/gold_candidates_discord_authored.csv \
  --write-csv \
  --min-score 0.55 \
  --q-thresh 0.5 \
  --max-lookahead 20 \
  --skip-acks \
  --debug

uv run python utils/harvest_gold_from_discord_authored.py \
  --threads-jsonl external/discord/stripped/issues.jsonl \
  --out-jsonl eval/data/gold_candidates_discord_authored.jsonl \
  --out-csv   eval/data/gold_candidates_discord_authored.csv \
  --write-csv \
  --min-score 0.55 \
  --q-thresh 0.5 \
  --max-lookahead 20 \
  --max-q-chars 600 \
  --max-a-chars 1200 \
  --max-prepend-blocks 2 \
  --max-append-blocks 3 \
  --skip-acks \
  --debug


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
ACK_RE = re.compile(
    r"^(thanks|thank you|ok|okay|great|cool|nice|got it|works|awesome|perfect|cheers)[\W\d]*$",
    re.I,
)
URL_RE = re.compile(r"https?://\S+")
CODE_RE = re.compile(r"`[^`]+`|```[\s\S]+?```")

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def trim_to_chars(text: str, limit: int) -> tuple[str, bool]:
    """
    Trim to ~limit chars, preferring sentence boundaries; returns (trimmed, was_trimmed)
    """
    s = text.strip()
    if limit <= 0 or len(s) <= limit:
        return s, False
    # Try to cut at last sentence boundary before limit
    cut = s[:limit]
    parts = SENT_SPLIT.split(cut)
    if len(parts) > 1:
        # rejoin all complete sentences except a possibly incomplete tail
        acc = ""
        total = 0
        for i, p in enumerate(parts):
            seg = (p + " ") if i < len(parts) - 1 else p
            if total + len(seg) > limit:
                break
            acc += seg
            total += len(seg)
        acc = acc.strip()
        if acc:
            return acc + " …", True
    # fallback: hard cut
    return cut.rstrip() + " …", True


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
def harvest_thread_authored(
    thread: Dict,
    min_score: float,
    max_q: int,
    q_thresh: float = 0.6,
    max_lookahead: int = 12,
    allow_same_author: bool = False,
    skip_acks: bool = True,
    debug: bool = False,
    max_q_chars: int = 600,
    max_a_chars: int = 1200,
    max_prepend_blocks: int = 2,
    max_append_blocks: int = 2,
) -> List[Dict]:
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
    q_idxs = [(i, s) for (i, s) in q_idxs if s >= q_thresh]

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

        # Build QUESTION: include immediately previous blocks by the SAME author (capped)
        q_text_parts = [qb["text"]]
        j = qi - 1
        prepend_used = 0
        while (
            j >= 0
            and blocks[j]["author_id"] == asker
            and prepend_used < max_prepend_blocks
        ):
            q_text_parts.insert(0, blocks[j]["text"])
            j -= 1
            prepend_used += 1
        question_text = " ".join(q_text_parts).strip()

        # Build ANSWER: next block by a DIFFERENT author, plus their subsequent consecutive blocks
        ans_start = None
        look_limit = min(len(blocks), qi + 1 + max_lookahead)
        ans_start = next(
            (
                k
                for k in range(qi + 1, look_limit)
                if (
                    (not skip_acks or not ACK_RE.match(blocks[k]["text"].strip()))
                    and (
                        (blocks[k]["author_id"] and blocks[k]["author_id"] != asker)
                        or (not blocks[k]["author_id"])
                        or allow_same_author
                    )
                )
            ),
            None,
        )

        if ans_start is None:
            if debug:
                print(
                    f"[DEBUG] thread={thread.get('id','?')} | qi={qi} | no answer within {max_lookahead} blocks"
                )
            continue

        answerer = blocks[ans_start]["author_id"]
        a_text_parts = [blocks[ans_start]["text"]]
        k = ans_start + 1
        append_used = 0
        while (
            k < len(blocks)
            and blocks[k]["author_id"] == answerer
            and append_used < max_append_blocks
        ):
            a_text_parts.append(blocks[k]["text"])
            k += 1
            append_used += 1
        answer_text = " ".join(a_text_parts).strip()
        if not answer_text:
            continue

        # --- NEW: Trim here ---
        q_trimmed, q_was_trimmed = trim_to_chars(question_text, max_q_chars)
        a_trimmed, a_was_trimmed = trim_to_chars(answer_text, max_a_chars)

        # Score (use trimmed answer for scoring)
        a_base = sent_score_answer(a_trimmed)
        if URL_RE.search(a_trimmed):
            a_base += 0.1
        if CODE_RE.search(a_trimmed):
            a_base += 0.1
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
            "question": q_trimmed,
            "proposed_answer": a_trimmed,
            "source_url": thread.get("url"),
            "timestamp": thread.get("timestamp", ""),
            "method": "discord_authored_blocks",
            "score": round(final, 2),
            "q_block": qi,
            "a_block": ans_start,
            "asker_id": asker,
            "answerer_id": answerer,
            "meta": {
                "q_len": len(question_text),
                "a_len": len(answer_text),
                "q_trimmed": q_was_trimmed,
                "a_trimmed": a_was_trimmed,
                "prepend_blocks_used": prepend_used,
                "append_blocks_used": append_used,
            },
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
        "--out-jsonl", default="eval/data/gold_candidates_discord_authored.jsonl"
    )
    ap.add_argument(
        "--out-csv", default="eval/data/gold_candidates_discord_authored.csv"
    )
    ap.add_argument("--min-score", type=float, default=0.62)
    ap.add_argument("--max-q-per-thread", type=int, default=5)
    ap.add_argument("--write-csv", action="store_true")
    ap.add_argument(
        "--q-thresh", type=float, default=0.6, help="Question threshold (default 0.6)"
    )
    ap.add_argument(
        "--a-thresh",
        type=float,
        default=0.0,
        help="(Reserved) Answer threshold, influences scoring only",
    )
    ap.add_argument(
        "--max-lookahead",
        type=int,
        default=12,
        help="Blocks to look ahead for an answer (default 12)",
    )
    ap.add_argument(
        "--allow-same-author", action="store_true", help="Allow same-author answers"
    )
    ap.add_argument(
        "--skip-acks", action="store_true", help="Skip short ack blocks as answers"
    )
    ap.add_argument("--debug", action="store_true", help="Print per-thread debug stats")
    ap.add_argument(
        "--max-q-chars", type=int, default=600, help="Cap question text length (chars)"
    )
    ap.add_argument(
        "--max-a-chars", type=int, default=1200, help="Cap answer text length (chars)"
    )
    ap.add_argument(
        "--max-prepend-blocks",
        type=int,
        default=2,
        help="Max previous same-author blocks to include in the question",
    )
    ap.add_argument(
        "--max-append-blocks",
        type=int,
        default=2,
        help="Max subsequent same-author blocks to include in the answer",
    )

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
            th,
            min_score=args.min_score,
            max_q=args.max_q_per_thread,
            q_thresh=args.q_thresh,
            max_lookahead=args.max_lookahead,
            allow_same_author=args.allow_same_author,
            skip_acks=args.skip_acks,
            debug=args.debug,
            max_q_chars=args.max_q_chars,
            max_a_chars=args.max_a_chars,
            max_prepend_blocks=args.max_prepend_blocks,
            max_append_blocks=args.max_append_blocks,
        )
        all_cands.extend(cands)

    print("Threads:", len(threads))
    print("With messages:", sum(1 for t in threads if t.get("messages")))

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
