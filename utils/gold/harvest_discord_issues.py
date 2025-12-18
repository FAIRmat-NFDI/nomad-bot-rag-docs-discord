#!/usr/bin/env python3
"""
Harvest summarized Q&A pairs from Discord issue threads.

This script scans DiscordChatExporter JSON files whose channel category is
`issues` and compresses each thread into a single Q&A pair. The goal is to
capture the full conversational context (instead of verbatim snippets) by
aggregating the first reporter message(s) into a question and summarizing the
maintainer replies into an answer.

Example usage:

```
uv run python utils/gold/harvest_discord_issues.py \
    --issues-glob \
    "/home/jfrudzinski/work/Discord/Analytics/nomad_discord_Q*_202*/NOMAD - issues - *.json" \
    --out-jsonl data/evaluation/gold_candidates_discord_issues.jsonl \
    --out-csv data/evaluation/gold_candidates_discord_issues.csv \
    --write-csv
```
"""

from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence


MENTION_PATTERN = re.compile(r"<@!?\\d+>|@\\w+")
QUOTE_PATTERN = re.compile(r"^>.*$", re.MULTILINE)
WHITESPACE_PATTERN = re.compile(r"\\s+")


def clean_text(text: str) -> str:
    """Normalize Discord message content for summarization."""

    if not text:
        return ""
    text = MENTION_PATTERN.sub("", text)
    text = QUOTE_PATTERN.sub("", text)
    text = text.replace("```", " ").replace("`", " ")
    text = text.replace("\\u200b", " ")  # zero-width spaces
    text = WHITESPACE_PATTERN.sub(" ", text)
    return text.strip()


def join_sentences(parts: Sequence[str], max_parts: int = 3) -> str:
    """Join message snippets into a natural sentence block."""

    trimmed = [p for p in parts if p]
    if not trimmed:
        return ""
    limited = trimmed[:max_parts]
    return " ".join(limited).strip()


def summarize_thread(data: Dict, source_path: Path) -> Optional[Dict]:
    """Convert one Discord issue thread into a Q&A candidate."""

    messages = [m for m in data.get("messages", []) if m.get("content")]
    if len(messages) < 3:
        return None

    # Sort by timestamp to be safe
    messages.sort(key=lambda m: m.get("timestamp", ""))

    # Determine reporter / original author
    question_author = None
    question_chunks: List[str] = []

    for msg in messages:
        author = msg.get("author") or {}
        if author.get("isBot"):
            continue
        question_author = author.get("id")
        question_chunks.append(clean_text(msg.get("content", "")))
        break

    if not question_author or not question_chunks:
        return None

    # Include follow-up messages from the reporter before someone else replies
    for msg in messages[1:]:
        author = msg.get("author") or {}
        if author.get("id") == question_author:
            question_chunks.append(clean_text(msg.get("content", "")))
        else:
            break

    question_body = join_sentences(question_chunks, max_parts=2)
    if not question_body:
        return None

    channel = data.get("channel", {})
    thread_title = channel.get("name") or "Unknown issue"
    question = question_body.strip()
    if not question.endswith("?"):
        question += "?"

    # Aggregate answers from other participants
    answer_parts: List[str] = []
    for msg in messages:
        author = msg.get("author") or {}
        if author.get("id") in (None, question_author):
            continue
        if author.get("isBot"):
            continue
        text = clean_text(msg.get("content", ""))
        if len(text) < 30:
            continue
        answer_parts.append(text)
        if len(answer_parts) >= 4:
            break

    if not answer_parts:
        return None

    answer = " ".join(answer_parts).strip()

    score = 0.55
    q_words = len(question.split())
    a_words = len(answer.split())
    if 25 <= q_words <= 180:
        score += 0.1
    if 60 <= a_words <= 400:
        score += 0.2
    if len(answer_parts) > 1:
        score += 0.05
    score = round(min(score, 0.95), 2)

    record = {
        "id": hashlib.sha1((str(source_path)).encode("utf-8")).hexdigest()[:16],
        "question": question,
        "answer": answer,
        "thread_title": thread_title,
        "message_count": len(messages),
        "source_file": str(source_path),
        "score": score,
    }
    return record


def write_outputs(records: List[Dict], out_jsonl: Path, out_csv: Optional[Path]):
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    if out_csv:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        cols = [
            "question",
            "answer",
            "thread_title",
            "message_count",
            "source_file",
            "score",
            "id",
        ]
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            for rec in records:
                writer.writerow({k: rec.get(k, "") for k in cols})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize Discord issue threads into Q&A pairs"
    )
    parser.add_argument(
        "--issues-glob",
        required=True,
        help="Glob pattern pointing to DiscordChatExporter JSON files for issue threads",
    )
    parser.add_argument(
        "--out-jsonl",
        type=Path,
        default=Path("data/evaluation/gold_candidates_discord_issues.jsonl"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("data/evaluation/gold_candidates_discord_issues.csv"),
    )
    parser.add_argument(
        "--write-csv", action="store_true", help="Write the CSV companion output"
    )
    args = parser.parse_args()

    files = sorted(glob.glob(args.issues_glob))
    if not files:
        raise SystemExit(f"No issue JSON files found for pattern: {args.issues_glob}")

    records: List[Dict] = []
    for path_str in files:
        path = Path(path_str)
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("channel", {}).get("category") != "issues":
            continue
        rec = summarize_thread(data, path)
        if rec:
            records.append(rec)

    # Deduplicate by normalized question text
    uniq: Dict[str, Dict] = {}
    for rec in records:
        key = rec["question"].strip().lower()
        if key not in uniq or rec["score"] > uniq[key].get("score", 0):
            uniq[key] = rec

    final_records = sorted(
        uniq.values(), key=lambda x: x.get("score", 0), reverse=True
    )

    write_outputs(final_records, args.out_jsonl, args.out_csv if args.write_csv else None)
    print(f"Harvested {len(final_records)} issue Q&A candidates")


if __name__ == "__main__":
    main()
