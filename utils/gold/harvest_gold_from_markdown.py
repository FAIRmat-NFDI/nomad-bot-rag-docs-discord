#!/usr/bin/env python3
"""
Harvest Q&A candidates from Markdown documentation files.

Input:  data/fetched/**/md/*.md
Output: data/evaluation/gold_candidates_docs_2025.jsonl (+ optional CSV)

Heuristics:
- Heading questions (H2/H3): ends with "?" or starts with (how/what/why/...)
- FAQ-like patterns in markdown
- Inline question sentences followed by explanatory paragraphs
- "How to ..." sections

Example usage:
uv run python utils/gold/harvest_gold_from_markdown.py \
  --md-root data/fetched \
  --min-score 0.55 \
  --max-candidates 150 \
  --write-csv
"""

from pathlib import Path
import re, json, csv, argparse, hashlib
from typing import List, Tuple, Dict

MD_ROOT_DEFAULT = "data/fetched"
OUT_JSONL = Path("data/evaluation/gold_candidates_docs_2025.jsonl")
OUT_CSV = Path("data/evaluation/gold_candidates_docs_2025.csv")

QUESTION_STARTS = (
    "how ", "what ", "why ", "can ", "is ", "are ", "should ", "does ",
    "where ", "when ", "which ", "who ", "could ", "would ",
    "how do", "how to", "how can", "what is", "what are", "why does",
)

BANNED_QUESTION_PHRASES = (
    "what you will learn",
    "what you'll do",
    "how to use this plugin",
    "how to cite this work",
    "any questions or suggestions",
    "who is this tutorial for?",
    "what should you know before this tutorial?",
)

COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def normalize_space(s: str) -> str:
    if not s:
        return ""
    without_comments = COMMENT_RE.sub(" ", s)
    return re.sub(r"\s+", " ", without_comments).strip()


def normalize_question_key(text: str) -> str:
    return normalize_space(text).lower()


def is_question_like(text: str) -> bool:
    if not text:
        return False
    t = text.strip()
    lt = t.lower()
    return t.endswith("?") or any(lt.startswith(p) for p in QUESTION_STARTS)


def is_banned_question(text: str) -> bool:
    if not text:
        return False
    lt = text.lower()
    return any(phrase in lt for phrase in BANNED_QUESTION_PHRASES)


def hash_id(*parts) -> str:
    h = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()[:16]
    return h


def score_candidate(question: str, answer: str, method: str) -> float:
    """Score based on question quality, answer length, and method confidence"""
    score = 0.5  # base
    
    # Question quality
    q_lower = question.lower()
    if question.endswith("?"):
        score += 0.15
    if any(q_lower.startswith(p) for p in QUESTION_STARTS):
        score += 0.1
    if len(question.split()) >= 4:
        score += 0.05
    
    # Answer quality
    ans_words = len(answer.split())
    if 20 <= ans_words <= 500:
        score += 0.15
    elif ans_words > 500:
        score += 0.05
    elif ans_words < 10:
        score -= 0.2
    
    # Code/links in answer
    if re.search(r"`[^`]+`|```[\s\S]+?```", answer):
        score += 0.1
    if re.search(r"https?://", answer):
        score += 0.05
    
    # Method confidence
    if method == "heading_qa":
        score += 0.1
    elif method == "faq_pattern":
        score += 0.15
    
    return max(0.0, min(1.0, score))


def parse_markdown_sections(md_text: str) -> List[Dict]:
    """Parse markdown into sections based on headers"""
    sections = []
    lines = md_text.split("\n")
    
    current_section = {"level": 0, "heading": "", "content": []}
    
    for line in lines:
        # Match headers (# to ####)
        header_match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if header_match:
            if current_section["content"]:
                sections.append(current_section)
            
            level = len(header_match.group(1))
            heading = header_match.group(2).strip()
            current_section = {"level": level, "heading": heading, "content": []}
        else:
            current_section["content"].append(line)
    
    if current_section["content"]:
        sections.append(current_section)
    
    return sections


def extract_heading_questions(sections: List[Dict], base_url: str, repo_name: str) -> List[Dict]:
    """Extract Q&A pairs where headings are questions"""
    candidates = []
    
    for section in sections:
        heading = section["heading"]
        if not is_question_like(heading):
            continue
        if is_banned_question(heading):
            continue
        
        # Build answer from section content
        content = "\n".join(section["content"]).strip()
        if len(content) < 30:
            continue
        
        # Extract first few paragraphs/code blocks as answer
        answer_parts = []
        in_code_block = False
        para = []
        
        for line in section["content"]:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block and para:
                    answer_parts.append(" ".join(para))
                    para = []
            elif in_code_block:
                continue
            elif line.strip():
                para.append(line.strip())
            elif para:
                answer_parts.append(" ".join(para))
                para = []
                if len(answer_parts) >= 3:  # Limit to first 3 paragraphs
                    break
        
        if para:
            answer_parts.append(" ".join(para))
        
        answer = normalize_space(" ".join(answer_parts[:3]))
        if len(answer) < 30:
            continue
        
        score = score_candidate(heading, answer, "heading_qa")
        
        candidates.append({
            "id": hash_id(repo_name, heading, answer[:50]),
            "question": heading,
            "proposed_answer": answer,
            "source_url": base_url,
            "title": repo_name,
            "section": heading,
            "method": "heading_qa",
            "score": score
        })
    
    return candidates


def extract_faq_patterns(md_text: str, base_url: str, repo_name: str) -> List[Dict]:
    """Extract Q&A from FAQ-style patterns like **Q:** ... **A:** ..."""
    candidates = []
    
    # Pattern 1: **Q:** ... **A:** ...
    qa_pattern1 = r"\*\*Q(?:uestion)?:?\*\*\s*(.+?)\n\s*\*\*A(?:nswer)?:?\*\*\s*(.+?)(?=\n\*\*Q|\n\n\*\*Q|\Z)"
    for match in re.finditer(qa_pattern1, md_text, re.DOTALL | re.IGNORECASE):
        question = normalize_space(match.group(1))
        answer = normalize_space(match.group(2))
        
        if len(question) < 10 or len(answer) < 30:
            continue
        if is_banned_question(question):
            continue
        
        score = score_candidate(question, answer, "faq_pattern")
        
        candidates.append({
            "id": hash_id(repo_name, question, answer[:50]),
            "question": question,
            "proposed_answer": answer,
            "source_url": base_url,
            "title": repo_name,
            "section": "FAQ",
            "method": "faq_pattern",
            "score": score
        })
    
    # Pattern 2: Q: ... A: ... (without bold)
    qa_pattern2 = r"^Q:?\s*(.+?)\n\s*A:?\s*(.+?)(?=\n\nQ:|\Z)"
    for match in re.finditer(qa_pattern2, md_text, re.MULTILINE | re.DOTALL):
        question = normalize_space(match.group(1))
        answer = normalize_space(match.group(2))
        
        if len(question) < 10 or len(answer) < 30:
            continue
        
        score = score_candidate(question, answer, "faq_pattern")
        
        candidates.append({
            "id": hash_id(repo_name, question, answer[:50]),
            "question": question,
            "proposed_answer": answer,
            "source_url": base_url,
            "title": repo_name,
            "section": "FAQ",
            "method": "faq_pattern",
            "score": score
        })
    
    return candidates


def extract_inline_questions(sections: List[Dict], base_url: str, repo_name: str) -> List[Dict]:
    """Find inline question sentences followed by explanatory text"""
    candidates = []
    
    for section in sections:
        content = "\n".join(section["content"])
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        
        for i, para in enumerate(paragraphs):
            # Look for questions within paragraphs
            sentences = re.split(r'(?<=[.!?])\s+', para)
            
            for j, sent in enumerate(sentences):
                sent = sent.strip()
                if not is_question_like(sent) or len(sent) < 15:
                    continue
                if is_banned_question(sent):
                    continue
                
                # Gather answer from remaining text in paragraph + next paragraph
                answer_parts = sentences[j+1:] if j+1 < len(sentences) else []
                if i+1 < len(paragraphs):
                    answer_parts.append(paragraphs[i+1])
                
                answer = normalize_space(" ".join(answer_parts))
                if len(answer) < 30:
                    continue
                
                score = score_candidate(sent, answer, "inline_question")
                
                candidates.append({
                    "id": hash_id(repo_name, sent, answer[:50]),
                    "question": sent,
                    "proposed_answer": answer,
                    "source_url": base_url,
                    "title": repo_name,
                    "section": section["heading"] or "Introduction",
                    "method": "inline_question",
                    "score": score
                })
    
    return candidates


def harvest_from_md_file(md_path: Path, base_url_template: str) -> List[Dict]:
    """Extract all candidate Q&A pairs from a single markdown file"""
    try:
        md_text = md_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"⚠️  Failed to read {md_path}: {e}")
        return []
    
    # Construct repo name and URL
    parts = md_path.parts
    repo_idx = parts.index("fetched") + 1 if "fetched" in parts else 0
    repo_name = parts[repo_idx] if repo_idx < len(parts) else "unknown"
    
    # Build relative path for URL
    md_idx = parts.index("md") if "md" in parts else repo_idx
    rel_path = "/".join(parts[md_idx+1:])
    base_url = base_url_template.format(repo=repo_name, path=rel_path)
    
    candidates = []
    
    # Parse into sections
    sections = parse_markdown_sections(md_text)
    
    # Extract using different heuristics
    candidates.extend(extract_heading_questions(sections, base_url, repo_name))
    candidates.extend(extract_faq_patterns(md_text, base_url, repo_name))
    candidates.extend(extract_inline_questions(sections, base_url, repo_name))
    
    return candidates


def harvest_all_markdown(md_root: Path, base_url_template: str, min_score: float, max_candidates: int) -> List[Dict]:
    """Recursively harvest from all markdown files"""
    all_candidates = []
    md_files = list(md_root.rglob("**/*.md"))
    
    print(f"🔎 Found {len(md_files)} markdown files")
    
    for i, md_path in enumerate(md_files, 1):
        if i % 10 == 0:
            print(f"   Processing {i}/{len(md_files)}...")
        
        candidates = harvest_from_md_file(md_path, base_url_template)
        all_candidates.extend(candidates)
    
    print(f"📝 Harvested {len(all_candidates)} raw candidates")

    # Deduplicate on normalized question text (keep highest score)
    deduped = {}
    for cand in all_candidates:
        key = normalize_question_key(cand.get("question", ""))
        if not key:
            continue
        if key not in deduped or cand.get("score", 0) > deduped[key].get("score", 0):
            deduped[key] = cand
    all_candidates = list(deduped.values())
    print(f"🔁 After deduplication: {len(all_candidates)} unique questions")

    # Filter by score
    filtered = [c for c in all_candidates if c["score"] >= min_score]
    print(f"✅ Kept {len(filtered)} candidates with score ≥ {min_score}")
    
    # Sort by score descending and limit
    filtered.sort(key=lambda x: x["score"], reverse=True)
    if len(filtered) > max_candidates:
        filtered = filtered[:max_candidates]
        print(f"🔝 Limited to top {max_candidates} candidates")
    
    return filtered


def write_jsonl(records: List[Dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_csv(records: List[Dict], path: Path):
    if not records:
        return
    
    cols = ["keep", "question", "proposed_answer", "source_url", "title", "section", "method", "score", "id"]
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            row = {"keep": "", **{k: r.get(k, "") for k in cols if k != "keep"}}
            w.writerow(row)


def main():
    ap = argparse.ArgumentParser(description="Harvest Q&A candidates from markdown documentation")
    ap.add_argument("--md-root", default=MD_ROOT_DEFAULT, help="Root dir of fetched markdown repos")
    ap.add_argument("--base-url-template", default="https://github.com/FAIRmat-NFDI/{repo}/blob/main/{path}",
                    help="URL template for source links")
    ap.add_argument("--min-score", type=float, default=0.5, help="Minimum score threshold")
    ap.add_argument("--max-candidates", type=int, default=150, help="Maximum number of candidates to keep")
    ap.add_argument("--write-csv", action="store_true", help="Also write CSV for review")
    args = ap.parse_args()
    
    root = Path(args.md_root)
    if not root.exists():
        raise SystemExit(f"❌ MD root not found: {root}")
    
    candidates = harvest_all_markdown(root, args.base_url_template, args.min_score, args.max_candidates)
    
    write_jsonl(candidates, OUT_JSONL)
    print(f"💾 Wrote JSONL: {OUT_JSONL}")
    
    if args.write_csv:
        write_csv(candidates, OUT_CSV)
        print(f"📄 Wrote CSV:   {OUT_CSV}")
    
    print(f"\n✨ Done! Generated {len(candidates)} candidates for manual review.")


if __name__ == "__main__":
    main()
