#!/usr/bin/env python3
"""
Generate ~200 gold Q&A candidates from multiple sources for manual review.

Sources:
1. Documentation markdown files (data/fetched/**/README.md, docs/*.md)
2. Discord chat exports (Discord/Analytics/nomad_discord_*)
3. Existing gold candidates that need review

Output:
- data/evaluation/gold_candidates_docs_BATCH.jsonl
- data/evaluation/gold_candidates_docs_BATCH.csv
- data/evaluation/gold_candidates_discord_BATCH.jsonl
- data/evaluation/gold_candidates_discord_BATCH.csv

Usage:
    uv run python utils/gold/generate_gold_candidates.py --batch 2025-12-17
"""

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# === Configuration ===
DOCS_ROOT = Path("data/fetched")
DISCORD_ROOT = Path("/home/jfrudzinski/work/Discord/Analytics")
EVAL_DIR = Path("data/evaluation")

QUESTION_STARTS = (
    "how ", "what ", "why ", "can ", "is ", "are ", "should ", "does ",
    "where ", "when ", "which ", "who ", "could ", "would ",
    "how do", "how to", "how can", "what is", "what are", "why does",
    "do i", "do you", "does the", "can i", "can you", "is there", "are there"
)


def normalize_space(s: str) -> str:
    """Normalize whitespace in text"""
    return re.sub(r"\s+", " ", (s or "").strip())


def hash_id(*parts) -> str:
    """Generate consistent short hash ID"""
    return hashlib.sha1("||".join(str(p) for p in parts).encode()).hexdigest()[:12]


def is_question_like(text: str) -> bool:
    """Check if text looks like a question"""
    if not text:
        return False
    t = text.strip()
    lt = t.lower()
    return t.endswith("?") or any(lt.startswith(p) for p in QUESTION_STARTS)


def score_candidate(question: str, answer: str, method: str) -> float:
    """Score candidate quality (0-1)"""
    score = 0.5
    
    # Question quality
    q_lower = question.lower()
    if question.endswith("?"):
        score += 0.15
    if any(q_lower.startswith(p) for p in QUESTION_STARTS):
        score += 0.1
    if len(question.split()) >= 5:
        score += 0.05
    
    # Answer quality
    ans_words = len(answer.split())
    if 30 <= ans_words <= 400:
        score += 0.2
    elif 20 <= ans_words < 30:
        score += 0.1
    elif ans_words < 15:
        score -= 0.3
    
    # Technical content
    if re.search(r"`[^`]+`|```[\s\S]+?```", answer):
        score += 0.1
    if re.search(r"https?://\S+", answer):
        score += 0.05
    
    # Method bonus
    if method in ["faq", "heading_qa"]:
        score += 0.1
    
    return max(0.0, min(1.0, score))


# === Documentation Harvesting ===

def extract_from_readme(readme_path: Path, repo_name: str) -> List[Dict]:
    """Extract Q&A candidates from README files"""
    candidates = []
    
    try:
        text = readme_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"⚠️  Could not read {readme_path}: {e}")
        return []
    
    # Parse sections
    sections = []
    current = {"level": 0, "heading": "", "content": []}
    
    for line in text.split("\n"):
        if match := re.match(r"^(#{1,4})\s+(.+)$", line):
            if current["content"]:
                sections.append(current)
            level = len(match.group(1))
            heading = match.group(2).strip()
            current = {"level": level, "heading": heading, "content": []}
        else:
            current["content"].append(line)
    
    if current["content"]:
        sections.append(current)
    
    # Extract heading-based Q&A
    for sec in sections:
        heading = sec["heading"]
        if not is_question_like(heading):
            continue
        
        # Build answer from content
        content_text = "\n".join(sec["content"]).strip()
        if len(content_text) < 40:
            continue
        
        # Extract first 3 paragraphs
        paragraphs = []
        current_para = []
        in_code = False
        
        for line in sec["content"]:
            if line.strip().startswith("```"):
                in_code = not in_code
                if not in_code and current_para:
                    paragraphs.append(" ".join(current_para))
                    current_para = []
            elif not in_code and line.strip():
                current_para.append(line.strip())
            elif not in_code and current_para:
                paragraphs.append(" ".join(current_para))
                current_para = []
                if len(paragraphs) >= 3:
                    break
        
        if current_para:
            paragraphs.append(" ".join(current_para))
        
        answer = normalize_space(" ".join(paragraphs[:3]))
        if len(answer) < 40:
            continue
        
        score = score_candidate(heading, answer, "heading_qa")
        
        if score >= 0.5:
            candidates.append({
                "id": f"docs-{hash_id(repo_name, heading)}",
                "question": heading,
                "proposed_answer": answer,
                "source_url": f"https://github.com/FAIRmat-NFDI/{repo_name}",
                "repo": repo_name,
                "file": readme_path.name,
                "method": "heading_qa",
                "score": round(score, 2)
            })
    
    return candidates


def harvest_documentation(max_per_repo: int = 5) -> List[Dict]:
    """Harvest Q&A from all documentation repos"""
    print("\n📚 Harvesting documentation sources...")
    
    all_candidates = []
    repo_counts = defaultdict(int)
    
    # Get all README and docs markdown files
    md_files = []
    for pattern in ["**/README.md", "**/docs/**/*.md", "**/*.md"]:
        md_files.extend(DOCS_ROOT.glob(pattern))
    
    print(f"   Found {len(md_files)} markdown files")
    
    for md_path in sorted(set(md_files)):
        # Determine repo name
        parts = md_path.relative_to(DOCS_ROOT).parts
        repo_name = parts[0] if parts else "unknown"
        
        # Skip if we have enough from this repo
        if repo_counts[repo_name] >= max_per_repo:
            continue
        
        candidates = extract_from_readme(md_path, repo_name)
        
        # Add top candidates from this file
        for cand in sorted(candidates, key=lambda x: x["score"], reverse=True)[:2]:
            if repo_counts[repo_name] < max_per_repo:
                all_candidates.append(cand)
                repo_counts[repo_name] += 1
    
    print(f"   ✓ Extracted {len(all_candidates)} candidates from {len(repo_counts)} repos")
    return all_candidates


# === Discord Harvesting ===

def extract_discord_qa(discord_file: Path) -> List[Dict]:
    """Extract Q&A from Discord chat export (JSONL format)"""
    candidates = []
    
    try:
        with discord_file.open() as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                # Look for question-answer patterns
                question = record.get("question", "")
                answer = record.get("proposed_answer") or record.get("gold_answer", "")
                
                if not question or not answer:
                    continue
                
                if not is_question_like(question):
                    continue
                
                # Clean up
                question = normalize_space(question)
                answer = normalize_space(answer)
                
                if len(question) < 15 or len(answer) < 30:
                    continue
                
                score = score_candidate(question, answer, "discord_qa")
                
                if score >= 0.5:
                    candidates.append({
                        "id": f"discord-{hash_id(discord_file.stem, question)}",
                        "question": question,
                        "proposed_answer": answer,
                        "source_file": discord_file.name,
                        "thread_id": record.get("thread_id", ""),
                        "title": record.get("title", ""),
                        "method": "discord_qa",
                        "score": round(score, 2)
                    })
        
    except Exception as e:
        print(f"   ⚠️  Error reading {discord_file}: {e}")
    
    return candidates


def harvest_discord(max_total: int = 100) -> List[Dict]:
    """Harvest Q&A from Discord chat exports"""
    print("\n💬 Harvesting Discord sources...")
    
    all_candidates = []
    
    # Find Discord export files
    discord_files = []
    if DISCORD_ROOT.exists():
        discord_files = list(DISCORD_ROOT.glob("nomad_discord_Q*_202*/*.jsonl"))
        discord_files.extend(DISCORD_ROOT.glob("nomad_discord_Q*_202*/**/*.jsonl"))
    
    print(f"   Found {len(discord_files)} Discord export files")
    
    for discord_file in sorted(discord_files):
        candidates = extract_discord_qa(discord_file)
        all_candidates.extend(candidates)
        
        if len(all_candidates) >= max_total * 1.5:  # Get extra for filtering
            break
    
    # Deduplicate by question similarity
    seen_questions = set()
    unique_candidates = []
    
    for cand in sorted(all_candidates, key=lambda x: x["score"], reverse=True):
        # Simple dedup: first 50 chars of question
        q_key = cand["question"][:50].lower()
        if q_key not in seen_questions:
            seen_questions.add(q_key)
            unique_candidates.append(cand)
            if len(unique_candidates) >= max_total:
                break
    
    print(f"   ✓ Extracted {len(unique_candidates)} unique candidates")
    return unique_candidates


# === Main Generation ===

def write_candidates(candidates: List[Dict], jsonl_path: Path, csv_path: Path):
    """Write candidates to JSONL and CSV"""
    # Write JSONL
    with jsonl_path.open("w") as f:
        for cand in candidates:
            f.write(json.dumps(cand) + "\n")
    
    # Write CSV
    if candidates:
        keys = list(candidates[0].keys())
        with csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(candidates)
    
    print(f"   📄 Wrote {len(candidates)} candidates")
    print(f"      → {jsonl_path}")
    print(f"      → {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate gold Q&A candidates")
    parser.add_argument("--batch", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Batch identifier (default: today's date)")
    parser.add_argument("--docs-target", type=int, default=100,
                        help="Target number of documentation candidates")
    parser.add_argument("--discord-target", type=int, default=100,
                        help="Target number of Discord candidates")
    
    args = parser.parse_args()
    
    print(f"\n🎯 Generating gold candidates (batch: {args.batch})")
    print(f"   Targets: {args.docs_target} docs + {args.discord_target} Discord = ~{args.docs_target + args.discord_target} total")
    
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Harvest documentation
    docs_candidates = harvest_documentation(max_per_repo=10)
    
    # Sort by score and take top N
    docs_candidates = sorted(docs_candidates, key=lambda x: x["score"], reverse=True)[:args.docs_target]
    
    docs_jsonl = EVAL_DIR / f"gold_candidates_docs_{args.batch}.jsonl"
    docs_csv = EVAL_DIR / f"gold_candidates_docs_{args.batch}.csv"
    
    print(f"\n💾 Writing documentation candidates...")
    write_candidates(docs_candidates, docs_jsonl, docs_csv)
    
    # 2. Harvest Discord
    discord_candidates = harvest_discord(max_total=args.discord_target)
    
    discord_jsonl = EVAL_DIR / f"gold_candidates_discord_{args.batch}.jsonl"
    discord_csv = EVAL_DIR / f"gold_candidates_discord_{args.batch}.csv"
    
    print(f"\n💾 Writing Discord candidates...")
    write_candidates(discord_candidates, discord_jsonl, discord_csv)
    
    # 3. Summary
    total = len(docs_candidates) + len(discord_candidates)
    print(f"\n✅ Generation complete!")
    print(f"   📊 Total candidates: {total}")
    print(f"      • Documentation: {len(docs_candidates)}")
    print(f"      • Discord: {len(discord_candidates)}")
    print(f"\n📝 Next steps:")
    print(f"   1. Review CSV files in Excel/LibreOffice")
    print(f"   2. Mark approved candidates (add 'approved' column)")
    print(f"   3. Convert to gold_all.jsonl format")
    print(f"\n   Review files:")
    print(f"   • {docs_csv}")
    print(f"   • {discord_csv}")


if __name__ == "__main__":
    main()
