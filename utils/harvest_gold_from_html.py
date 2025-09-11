#!/usr/bin/env python3
"""
Harvest candidate Q&A from a built MkDocs (Material) site snapshot.

Input:  root of HTML files (e.g., external/html/)
Output: eval/data/gold_candidates.jsonl  (+ optional CSV for review)

Heuristics:
- Heading questions (H2/H3): ends with "?" or starts with (how/what/why/…)
- FAQ blocks (<details>, dl/dt-dd) when present
- Inline question sentences within paragraphs
- "How to ..." sections/pages

Example usage:

# Ensure you fetched the HTML snapshot already (e.g., external/html/)
uv run python utils/harvest_gold_from_html.py \
  --html-root external/nomad-docs/html \
  --base-url https://fairmat-nfdi.github.io/nomad-docs \
  --min-score 0.55 \
  --write-csv

Each candidate includes a rough score for triage and a source URL anchor.
"""

from pathlib import Path
from bs4 import BeautifulSoup
import re, json, csv, argparse, hashlib

HTML_ROOT_DEFAULT = "external/nomad-docs/html"
OUT_JSONL = Path("eval/data/gold_candidates.jsonl")
OUT_CSV = Path("eval/data/gold_review.csv")

QUESTION_STARTS = (
    "how ",
    "what ",
    "why ",
    "can ",
    "is ",
    "are ",
    "should ",
    "does ",
    "where ",
    "how do",
    "how to",
    "how can",
    "what is",
    "what are",
    "why does",
    "why do",
)


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def is_question_like(text: str) -> bool:
    if not text:
        return False
    t = text.strip()
    lt = t.lower()
    return t.endswith("?") or any(lt.startswith(p) for p in QUESTION_STARTS)


def tokenize_estimate(text: str) -> int:
    # cheap proxy: 1 token ~ 4 chars (English prose)
    return max(1, len(text) // 4)


def hash_id(*parts) -> str:
    h = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()[:16]
    return h


def get_article(soup: BeautifulSoup):
    # Material for MkDocs typical content container
    return (
        soup.select_one("article.md-content__inner.md-typeset")
        or soup.select_one("main article")
        or soup.select_one("article")
    )


def section_text(nodes) -> str:
    texts = []
    for n in nodes:
        name = getattr(n, "name", "")
        if name in ("p", "ul", "ol", "pre", "table", "blockquote", "div"):
            txt = n.get_text(" ", strip=True)
            if txt:
                texts.append(txt)
    return normalize_space(" ".join(texts))


def split_sections(article):
    # Return a list of (heading, id, nodes[]) split by H2/H3
    out, cur = [], {"heading": "", "id": "", "nodes": []}
    # H1 as page title
    h1 = article.find("h1")
    page_title = normalize_space(h1.get_text()) if h1 else ""
    for child in article.children:
        name = getattr(child, "name", None)
        if name in ("h2", "h3"):
            if cur["nodes"]:
                out.append(cur)
            cur = {
                "heading": normalize_space(child.get_text()),
                "id": child.get("id") or "",
                "nodes": [],
            }
        else:
            if name in (
                "p",
                "ul",
                "ol",
                "pre",
                "table",
                "blockquote",
                "div",
                "details",
                "dl",
            ):
                cur["nodes"].append(child)
    if cur["nodes"]:
        out.append(cur)
    return page_title, out


def extract_faq_pairs(section_nodes):
    """Try to find structured Q/A pairs inside a section: <details>, dl/dt-dd"""
    pairs = []
    # details/summary
    for det in [n for n in section_nodes if getattr(n, "name", "") == "details"]:
        summary = det.find("summary")
        q = normalize_space(summary.get_text(" ", strip=True) if summary else "")
        a = normalize_space(det.get_text(" ", strip=True).replace(q, "", 1))
        if q and len(a) > 20:
            pairs.append(("faq_block", q, a))

    # definition list dt->dd
    for dl in [n for n in section_nodes if getattr(n, "name", "") == "dl"]:
        dts = dl.find_all("dt")
        for dt in dts:
            q = normalize_space(dt.get_text(" ", strip=True))
            dd = dt.find_next_sibling("dd")
            a = normalize_space(dd.get_text(" ", strip=True)) if dd else ""
            if q and len(a) > 20:
                pairs.append(("faq_block", q, a))
    return pairs


def extract_inline_questions(section_nodes):
    """Find sentences ending with ? and grab following 1-3 paragraphs as answer."""
    candidates = []
    paras = [n for n in section_nodes if getattr(n, "name", "") == "p"]
    for i, p in enumerate(paras):
        text = normalize_space(p.get_text(" ", strip=True))
        # scan for question-like sentence
        for m in re.finditer(r"([^?]{8,200}?\?)", text):
            q = normalize_space(m.group(1))
            # answer = next 1-3 paragraphs
            ans_parts = []
            for j in range(i + 1, min(i + 4, len(paras))):
                ans_parts.append(normalize_space(paras[j].get_text(" ", strip=True)))
            a = normalize_space(" ".join(ans_parts))
            if len(a) > 20:
                candidates.append(("inline_q", q, a))
    return candidates


def build_answer_from_section(section_nodes):
    # Use first 1–2 paragraphs + bullet list and pre/code if present
    paras = [
        normalize_space(n.get_text(" ", strip=True))
        for n in section_nodes
        if getattr(n, "name", "") == "p"
    ]
    lists = [
        normalize_space(n.get_text(" ", strip=True))
        for n in section_nodes
        if getattr(n, "name", "") in ("ul", "ol")
    ]
    pres = [
        normalize_space(n.get_text(" ", strip=True))
        for n in section_nodes
        if getattr(n, "name", "") == "pre"
    ]
    parts = []
    if paras:
        parts.append(paras[0])
        if len(paras) > 1:
            parts.append(paras[1])
    if lists:
        parts.append(lists[0])
    if pres:
        parts.append(pres[0])
    a = normalize_space(" ".join(parts))
    return a


def score_candidate(method: str, q: str, a: str) -> float:
    s = 0.0
    if method == "heading_q":
        s += 0.5
    if method == "faq_block":
        s += 0.6
    if method == "inline_q":
        s += 0.3
    lt = len(a)
    if 200 <= lt <= 2000:
        s += 0.2  # reasonable length
    if re.search(r"\b(step|click|navigate|set|configure|example)\b", a, re.I):
        s += 0.05
    if re.search(r"```|code|shell|\$ ", a, re.I):
        s += 0.05
    if q.endswith("?"):
        s += 0.05
    return round(min(s, 1.0), 2)


def harvest_from_html(root: Path, base_url: str):
    out = []
    for html in root.rglob("*.html"):
        # skip theme/search/404
        sp = html.as_posix()
        if any(x in sp for x in ("/assets/", "/search/", "sitemap", "404.html")):
            continue
        soup = BeautifulSoup(html.read_text(encoding="utf-8"), "lxml")
        article = get_article(soup)
        if not article:
            continue

        page_title, sections = split_sections(article)
        rel = html.relative_to(root).as_posix()
        page_base = base_url.rstrip("/") + "/" + rel.replace("index.html", "")

        for sec in sections:
            heading = normalize_space(sec["heading"])
            sec_id = sec.get("id") or ""
            anchor = f"#{sec_id}" if sec_id else ""
            url = page_base + anchor

            # 1) FAQ pairs (highest precision)
            for method, q, a in extract_faq_pairs(sec["nodes"]):
                score = score_candidate(method, q, a)
                out.append(
                    {
                        "id": hash_id(rel, sec_id, q),
                        "question": q,
                        "proposed_answer": a,
                        "source_url": url,
                        "title": page_title,
                        "section": heading or page_title,
                        "method": method,
                        "score": score,
                    }
                )

            # 2) Heading questions
            if heading and is_question_like(heading):
                a = build_answer_from_section(sec["nodes"]) or section_text(
                    sec["nodes"]
                )
                if len(a) > 20:
                    score = score_candidate("heading_q", heading, a)
                    out.append(
                        {
                            "id": hash_id(rel, sec_id, heading),
                            "question": heading
                            if heading.endswith("?")
                            else f"{heading}?",
                            "proposed_answer": a,
                            "source_url": url,
                            "title": page_title,
                            "section": heading,
                            "method": "heading_q",
                            "score": score,
                        }
                    )

            # 3) Inline paragraph questions
            for method, q, a in extract_inline_questions(sec["nodes"]):
                score = score_candidate(method, q, a)
                out.append(
                    {
                        "id": hash_id(rel, sec_id, q),
                        "question": q,
                        "proposed_answer": a,
                        "source_url": url,
                        "title": page_title,
                        "section": heading or page_title,
                        "method": method,
                        "score": score,
                    }
                )

            # 4) How-to sections/pages (fallback)
            if heading.lower().startswith("how to ") and not is_question_like(heading):
                a = build_answer_from_section(sec["nodes"])
                q = heading if heading.endswith("?") else f"{heading}?"
                if len(a) > 20:
                    score = score_candidate("howto", q, a)
                    out.append(
                        {
                            "id": hash_id(rel, sec_id, q),
                            "question": q,
                            "proposed_answer": a,
                            "source_url": url,
                            "title": page_title,
                            "section": heading,
                            "method": "howto",
                            "score": score,
                        }
                    )

    # De-duplicate by normalized question text + url
    uniq = {}
    for r in out:
        key = (re.sub(r"\W+", " ", r["question"].lower()).strip(), r["source_url"])
        if key not in uniq or r["score"] > uniq[key]["score"]:
            uniq[key] = r
    return list(uniq.values())


def write_jsonl(records, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_csv(records, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "keep",
        "question",
        "proposed_answer",
        "source_url",
        "title",
        "section",
        "method",
        "score",
        "id",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            row = {"keep": "", **{k: r.get(k, "") for k in cols if k != "keep"}}
            w.writerow(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--html-root",
        default=HTML_ROOT_DEFAULT,
        help="Root dir of downloaded gh-pages HTML",
    )
    ap.add_argument(
        "--base-url",
        default="https://fairmat-nfdi.github.io/nomad-docs",
        help="Public base URL for citations",
    )
    ap.add_argument(
        "--min-score",
        type=float,
        default=0.5,
        help="Keep only candidates with score ≥ this",
    )
    ap.add_argument(
        "--write-csv", action="store_true", help="Also write CSV for human review"
    )
    args = ap.parse_args()

    root = Path(args.html_root)
    if not root.exists():
        raise SystemExit(f"HTML root not found: {root}")

    print(f"🔎 Scanning: {root}")
    recs = harvest_from_html(root, args.base_url)
    print(f"📝 Harvested {len(recs)} raw candidates")

    # Filter by score
    recs = [r for r in recs if r.get("score", 0) >= args.min_score]
    print(f"✅ Kept {len(recs)} candidates with score ≥ {args.min_score}")

    write_jsonl(recs, OUT_JSONL)
    print(f"💾 Wrote JSONL: {OUT_JSONL}")

    if args.write_csv:
        write_csv(recs, OUT_CSV)
        print(f"📄 Wrote CSV:   {OUT_CSV}")


if __name__ == "__main__":
    main()
