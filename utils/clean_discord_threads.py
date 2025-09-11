#!/usr/bin/env python3
"""
Clean Discord threads exported via DiscordChatExporter and produce a normalized JSONL
(1 line per thread) suitable for downstream harvesting/eval.

Features:
- Redact @mentions, emails, phone-like numbers
- Trim greetings/thanks/sign-offs and general chatty fluff
- Preserve code blocks verbatim
- Normalize timestamps to UTC ISO when possible
- Stable thread id

Usage examples
--------------
# Clean all threads under a raw export folder into JSONL:
uv run python utils/clean_discord_threads.py \
  --raw-dir /path/to/export/issues \
  --out-jsonl external/discord/stripped/issues.jsonl

# Or use a glob:
uv run python utils/clean_discord_threads.py \
  --raw-glob "/path/to/export/issues/*.json" \
  --out-jsonl external/discord/stripped/issues.jsonl \
  --min-msg-chars 3

# Disable fluff trimming but keep PII/mentions redaction:
uv run python utils/clean_discord_threads.py \
  --raw-dir /path/to/export/issues \
  --out-jsonl external/discord/stripped/issues.jsonl \
  --no-trim-fluff


Keep tokens (default):

uv run python utils/clean_discord_threads.py \
  --raw-dir "/path/to/issues" \
  --out-jsonl "external/discord/stripped/issues.jsonl" \
  --strip-greeting-names


Remove redacted content entirely + strip greeting names:

uv run python utils/clean_discord_threads.py \
  --raw-dir "/path/to/issues" \
  --out-jsonl "external/discord/stripped/issues.jsonl" \
  --redaction-mode remove \
  --strip-greeting-names
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

# ---------------- Timestamp ----------------


def to_utc_iso(ts: str) -> str:
    """
    Best-effort ISO8601 → UTC 'Z'. If parsing fails, return original.
    Handles timestamps like '2025-03-18T11:51:48.33+01:00'.
    """
    if not ts:
        return ""
    try:
        # Python 3.10 can handle fractional seconds, but if it fails we try padding
        dt = datetime.fromisoformat(ts)
        return (
            dt.astimezone(timezone.utc)
            .replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
    except Exception:
        # Try padding fractional seconds to microseconds if like ".33+01:00"
        m = re.match(r"^(.*T\d{2}:\d{2}:\d{2})(\.\d+)?([+-]\d{2}:\d{2}|Z)?$", ts)
        if m:
            base, frac, tz = m.groups()
            if frac and len(frac) < 7:  # e.g., .33 -> .330000
                frac = frac + "0" * (7 - len(frac))
            try_ts = f"{base}{frac or ''}{tz or ''}"
            try:
                dt = datetime.fromisoformat(try_ts)
                return (
                    dt.astimezone(timezone.utc)
                    .replace(tzinfo=timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z")
                )
            except Exception:
                return ts
        return ts


# ---------------- Cleaning & Redaction ----------------

CODEBLOCK_RE = re.compile(r"```[\s\S]*?```", re.M)
SIGNOFF_LINE_RE = re.compile(
    r"^\s*(thanks|thank you|many thanks|cheers|best(?: regards)?|kind regards|br|rgds|thx)[\.,!]*\s*$",
    re.I,
)
LEADING_FLUFF = [
    r"(?:hi|hey|hello|dear(?: all)?|good (?:morning|afternoon|evening))[,!.\s-]*",
    r"(?:thanks|thank you|many thanks|thx)[,!.\s-]*",
    r"(?:sorry(?: about that| for the late reply)?)[:,!.\s-]*",
    r"(?:quick question)[:\-\s]*",
    r"(?:i was (?:thinking|wondering|trying) about this)[:,\-\s]*",
    r"(?:i was (?:thinking|wondering|trying))[:,\-\s]*",
]
LEADING_FLUFF_RE = re.compile(r"^(?:" + r"|".join(LEADING_FLUFF) + r")", re.I)
MENTION_RE = re.compile(r"@\S+")
MULTI_PUNCT_RE = re.compile(r"([!?.,])\1{2,}")
WS_RE = re.compile(r"\s+")
ASCII_EMOJI_RE = re.compile(r"(:-\)|:-\(|;-\)|:\)|:\(|;-\))")
REDACTED_TOKEN_RE = re.compile(r"\[REDACTED_[A-Z]+\]")
# e.g., "hi John,", "hello Dr. Smith -", "dear Alice"
GREETING_NAME_RE = re.compile(
    r"""^\s*
        (?:(?:hi|hey|hello|dear)\b)          # greeting
        [\s,!:.-]*                           # punctuation/space
        (?:@?\w[\w.'-]*\s*){1,3}            # 1-3 name-like tokens (with @ allowed)
        [,:;.!-]*\s*                         # trailing punctuation/space
    """,
    re.I | re.X,
)


def apply_redaction_mode(text: str, mode: str) -> str:
    """If mode=='remove', drop redaction tokens entirely and tidy whitespace."""
    if mode == "remove":
        text = REDACTED_TOKEN_RE.sub("", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"(?:\s*\n\s*){2,}", "\n", text)
    return text.strip()


def normalize_name(name: str) -> str:
    s = (name or "").lstrip("@").strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[\u200b-\u200f\u202a-\u202e]", "", s)
    return s


def rewrite_mentions(text: str, mentions: list, redaction_mode: str = "token") -> str:
    if not text:
        return ""
    out = text
    # normalize known mentions
    reps = []
    for m in mentions or []:
        nick = m.get("nickname") or m.get("name")
        name = m.get("name")
        cands = []
        if nick:
            cands.append(nick)
        if name and name != nick:
            cands.append(name)
        uniq = sorted(set(cands), key=lambda s: len(s), reverse=True)
        norm = normalize_name(nick or name or "")
        if not norm:
            continue
        for cand in uniq:
            reps.append((r"@" + re.escape(cand), f"@{norm}"))
    seen, ordered = set(), []
    for pat, repl in reps:
        if pat not in seen:
            seen.add(pat)
            ordered.append((pat, repl))
    for pat, repl in ordered:
        out = re.sub(pat, repl, out)

    # redact remaining @mentions
    repl = "" if redaction_mode == "remove" else "[REDACTED_MENTION]"
    out = re.sub(r"@\S+", repl, out)
    return out


def redact_pii(text: str, redaction_mode: str = "token") -> str:
    email_repl = "" if redaction_mode == "remove" else "[REDACTED_EMAIL]"
    phone_repl = "" if redaction_mode == "remove" else "[REDACTED_PHONE]"
    text = re.sub(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", email_repl, text)
    text = re.sub(
        r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?){2,4}\d{2,4}\b",
        phone_repl,
        text,
    )
    return text


def _clean_noncode(
    chunk: str, do_trim_fluff: bool, strip_greeting_names: bool, redaction_mode: str
) -> str:
    if not chunk:
        return ""
    lines = [l for l in chunk.splitlines()]
    # drop pure sign-off/ack lines
    lines = [l for l in lines if not SIGNOFF_LINE_RE.match(l)]
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        # redact mentions (per mode)
        s = rewrite_mentions(
            s, mentions=[], redaction_mode=redaction_mode
        )  # no metadata here; just sweep leftovers

        if do_trim_fluff:
            # remove greeting name at start if enabled
            if strip_greeting_names:
                s = GREETING_NAME_RE.sub("", s)

            # strip generic leading fluff
            prev = None
            while prev != s:
                prev = s
                s = LEADING_FLUFF_RE.sub("", s).lstrip()

        s = ASCII_EMOJI_RE.sub("", s)
        s = MULTI_PUNCT_RE.sub(r"\1\1", s)  # cap repeats to 2
        lines[i] = s
        break  # only the first substantive line gets opener stripping

    # Collapse whitespace on all lines
    lines = [WS_RE.sub(" ", l).strip() for l in lines]
    lines = [l for l in lines if l]
    return "\n".join(lines) + ("\n" if chunk.endswith("\n") else "")


def trim_conversational_fluff(
    text: str,
    do_trim_fluff: bool = True,
    strip_greeting_names: bool = False,
    redaction_mode: str = "token",
) -> str:
    if not text:
        return ""
    rebuilt = []
    last = 0
    for m in CODEBLOCK_RE.finditer(text):
        pre = text[last : m.start()]
        code = text[m.start() : m.end()]
        rebuilt.append(
            _clean_noncode(pre, do_trim_fluff, strip_greeting_names, redaction_mode)
        )
        rebuilt.append(code)
        last = m.end()
    rebuilt.append(
        _clean_noncode(text[last:], do_trim_fluff, strip_greeting_names, redaction_mode)
    )
    cleaned = "".join(rebuilt).strip()
    return cleaned


# ---------------- Load & Normalize ----------------


def load_thread_as_text(
    path: Path,
    min_msg_chars: int,
    do_trim_fluff: bool,
    redaction_mode: str,
    strip_greeting_names: bool,
) -> Optional[Dict]:
    """
    Load a single DiscordChatExporter JSON thread, clean messages, and return a
    dict with concatenated cleaned text.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    guild = data.get("guild", {}) or {}
    channel = data.get("channel", {}) or {}
    msgs = data.get("messages", []) or []

    title = channel.get("name") or path.stem
    section = channel.get("category") or guild.get("name")
    first_ts = None

    texts: List[str] = []
    for m in msgs:
        t = (m.get("content") or "").strip()
        if not t:
            continue
        t = rewrite_mentions(t, m.get("mentions") or [], redaction_mode=redaction_mode)
        t = redact_pii(t, redaction_mode=redaction_mode)
        t = trim_conversational_fluff(
            t,
            do_trim_fluff=do_trim_fluff,
            strip_greeting_names=strip_greeting_names,
            redaction_mode=redaction_mode,
        )
        if len(t) < min_msg_chars:
            continue
        texts.append(t)
        if not first_ts:
            first_ts = to_utc_iso(m.get("timestamp"))

    full_text = "\n".join(texts).strip()
    full_text = apply_redaction_mode(full_text, redaction_mode)

    return {
        "source": "discord",
        "title": title,
        "section": section,
        "text": full_text,
        "url": None,
        "timestamp": first_ts or "",
    }


def thread_stable_id(thread: Dict) -> str:
    """Stable id from title + first timestamp + short hash of text."""
    base = f"{thread.get('title','')}|{thread.get('timestamp','')}"
    h = hashlib.sha1(thread.get("text", "").encode("utf-8")).hexdigest()[:10]
    return f"{base}|{h}"


def save_threads_jsonl(threads: List[Dict], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for th in threads:
            rec = {
                "id": thread_stable_id(th),
                "source": th.get("source", "discord"),
                "title": th.get("title", ""),
                "section": th.get("section", ""),
                "text": th.get("text", ""),
                "url": th.get("url"),
                "timestamp": th.get("timestamp", ""),
                "char_count": len(th.get("text", "")),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.replace(out_path)
    return out_path


# ---------------- CLI ----------------


def main():
    ap = argparse.ArgumentParser(description="Clean Discord threads → JSONL")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--raw-dir", help="Directory containing raw DiscordChatExporter JSON files"
    )
    g.add_argument(
        "--raw-glob", help="Glob for raw JSON files, e.g. '/path/issues/*.json'"
    )
    ap.add_argument(
        "--out-jsonl",
        required=True,
        help="Destination JSONL path (one record per thread)",
    )
    ap.add_argument(
        "--min-msg-chars", type=int, default=3, help="Drop messages shorter than this"
    )
    ap.add_argument(
        "--no-trim-fluff",
        action="store_true",
        help="Disable chatty fluff removal (keeps PII/mention redaction)",
    )
    ap.add_argument(
        "--max-threads",
        type=int,
        default=0,
        help="Optional cap on number of threads to process",
    )
    ap.add_argument(
        "--redaction-mode",
        choices=["token", "remove"],
        default="token",
        help="How to handle PII/mentions: 'token' → keep [REDACTED_*], 'remove' → delete completely.",
    )
    ap.add_argument(
        "--strip-greeting-names",
        action="store_true",
        help="Remove a name immediately following hello/hi/hey/dear at start of the message.",
    )
    args = ap.parse_args()

    # Collect input files
    if args.raw_dir:
        paths = sorted(Path(args.raw_dir).glob("*.json"))
    else:
        paths = [Path(p) for p in sorted(__import__("glob").glob(args.raw_glob))]

    if not paths:
        raise SystemExit("No JSON files found. Check --raw-dir/--raw-glob.")

    print(f"Found {len(paths)} JSON files to process")

    threads: List[Dict] = []
    for i, p in enumerate(paths, 1):
        th = load_thread_as_text(
            p,
            min_msg_chars=args.min_msg_chars,
            do_trim_fluff=not args.no_trim_fluff,
            redaction_mode=args.redaction_mode,
            strip_greeting_names=args.strip_greeting_names,
        )

        if th and th.get("text"):
            threads.append(th)
        if args.max_threads and len(threads) >= args.max_threads:  # guard if set
            break
        if i % 50 == 0 or i == len(paths):
            print(f"Processed {i}/{len(paths)} files … kept {len(threads)} threads")

    out_path = save_threads_jsonl(threads, Path(args.out_jsonl))
    print(f"✅ Saved {len(threads)} cleaned threads → {out_path}")


if __name__ == "__main__":
    main()
