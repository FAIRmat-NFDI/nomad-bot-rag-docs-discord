#!/usr/bin/env python3
"""
Build gold Q&A from the docs Glossary page.

Input:
  --html-root  path to your fetched repo HTML snapshot
               e.g. external/nomad-docs/html
  --base-url   public base URL for citations (default nomad docs site)

Output:
  eval/gold_nomad_glossary.jsonl  (appends; dedup by (term, source_url))

Question format:
  "What does <TERM> mean in NOMAD?"   (or "What is <TERM> in NOMAD?" if you prefer)
"""

import argparse, json, re
from pathlib import Path
from bs4 import BeautifulSoup


def norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def find_glossary_file(html_root: Path) -> Path | None:
    # Try typical locations
    candidates = [
        *html_root.rglob("reference/glossary.html"),
        *html_root.rglob("glossary.html"),
    ]
    return candidates[0] if candidates else None


def extract_terms(glossary_html: Path, base_url: str):
    soup = BeautifulSoup(glossary_html.read_text(encoding="utf-8"), "lxml")
    article = (
        soup.select_one("article.md-content__inner.md-typeset")
        or soup.select_one("main article")
        or soup.select_one("article")
    )
    if not article:
        return []

    terms = []
    children = list(article.children)

    # Build page URL for citation
    rel = glossary_html.relative_to(html_root).as_posix()
    page_url = f"{base_url.rstrip('/')}/{rel.replace('index.html','')}"

    i = 0
    while i < len(children):
        node = children[i]
        name = getattr(node, "name", None)
        if name in ("h2", "h3"):
            term = norm_text(node.get_text(" ", strip=True))
            term_id = node.get("id") or ""
            anchor = f"#{term_id}" if term_id else ""
            buf = []
            j = i + 1
            while j < len(children):
                n2 = children[j]
                n2name = getattr(n2, "name", None)
                if n2name in ("h2", "h3"):
                    break
                if n2name in ("p", "ul", "ol", "pre", "blockquote", "div"):
                    txt = norm_text(n2.get_text(" ", strip=True))
                    if txt:
                        buf.append(txt)
                j += 1
            if buf:
                short = buf[0]
                terms.append(
                    {"term": term, "definition": short, "url": page_url + anchor}
                )
            i = j
        else:
            i += 1
    return terms


def load_existing(path: Path):
    if not path.exists():
        return set()
    keys = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            term = (rec.get("meta") or {}).get("term") or ""
            url = rec.get("source_url", "")
            keys.add((term.lower().strip(), url))
    return keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--html-root",
        default="external/nomad-docs/html",
        help="Path to fetched gh-pages HTML snapshot (default: external/nomad-docs/html)",
    )
    ap.add_argument(
        "--base-url",
        default="https://fairmat-nfdi.github.io/nomad-docs",
        help="Public base URL for citations",
    )
    ap.add_argument(
        "--out", default="eval/gold_nomad_glossary.jsonl", help="Output JSONL path"
    )
    ap.add_argument(
        "--question-style",
        choices=["what_is", "what_does_mean"],
        default="what_does_mean",
        help="Question template style",
    )
    args = ap.parse_args()

    global html_root
    html_root = Path(args.html_root)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    glossary = find_glossary_file(html_root)
    if not glossary:
        raise SystemExit(f"❌ Glossary HTML not found under {html_root}")

    terms = extract_terms(glossary, args.base_url)
    print(f"🧾 Extracted {len(terms)} glossary items")

    existing = load_existing(out_path)
    added = 0
    with out_path.open("a", encoding="utf-8") as f:
        for t in terms:
            key = (t["term"].lower().strip(), t["url"])
            if key in existing:
                continue
            q = (
                f"What is {t['term']} in NOMAD?"
                if args.question_style == "what_is"
                else f"What does {t['term']} mean in NOMAD?"
            )
            rec = {
                "question": q,
                "gold_answer": t["definition"],
                "gold_urls": [t["url"]],
                "source_url": t["url"],
                "title": "Glossary",
                "section": t["term"],
                "meta": {"type": "glossary", "term": t["term"]},
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            existing.add(key)
            added += 1
    print(f"✅ Wrote {added} new entries to {out_path}")


if __name__ == "__main__":
    main()
