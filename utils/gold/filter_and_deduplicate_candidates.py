#!/usr/bin/env python3
"""
Filter and deduplicate gold candidates to a manageable review set.

Applies:
1. Exact question deduplication (keep highest score)
2. Quality filters (answer length, technical content)
3. Diversity sampling (limit per source/channel)
4. Target size reduction (~200 candidates)

Usage:
    uv run python utils/gold/filter_and_deduplicate_candidates.py \
        --docs-in data/evaluation/gold_candidates_docs_2025-12-17.jsonl \
        --discord-in data/evaluation/gold_candidates_discord_2025-12-17.jsonl \
        --docs-out data/evaluation/gold_candidates_docs_filtered_2025-12-17.jsonl \
        --discord-out data/evaluation/gold_candidates_discord_filtered_2025-12-17.jsonl \
        --target-docs 80 \
        --target-discord 120 \
        --write-csv
"""

import argparse
import json
import csv
import re
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load JSONL file into list of dicts."""
    candidates = []
    with path.open() as f:
        for line in f:
            if line.strip():
                candidates.append(json.loads(line))
    return candidates


def write_jsonl(candidates: List[Dict[str, Any]], path: Path):
    """Write candidates to JSONL file."""
    with path.open('w') as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')


def write_csv(candidates: List[Dict[str, Any]], path: Path):
    """Write candidates to CSV file."""
    if not candidates:
        return
    
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=candidates[0].keys())
        writer.writeheader()
        writer.writerows(candidates)


def normalize_question(q: str) -> str:
    """Normalize question for fuzzy matching."""
    # Convert to lowercase, remove extra whitespace, strip punctuation
    q = q.lower().strip()
    q = re.sub(r'\s+', ' ', q)
    q = re.sub(r'[^\w\s]', '', q)
    return q


def requires_context(text: str) -> bool:
    """Check if question/answer requires external context."""
    text_lower = text.lower()
    
    # Phrases that indicate dependency on previous context
    context_phrases = [
        'above', 'below', 'previous', 'earlier', 'mentioned',
        'as discussed', 'as we discussed', 'as i said', 'as you said',
        'see above', 'see below', 'check above', 'look above',
        'corresponding', 'this message', 'that message',
        'the screenshot', 'the image', 'the attachment',
        'this issue', 'that issue', 'this problem', 'that problem',
        'this error', 'that error', 'same error', 'same issue',
        'my code', 'your code', 'my example', 'your example',
        'like this', 'like that', 'such as this', 'such as that',
        'this part:', 'that part:', 'this section', 'that section',
    ]
    
    # Questions that request sharing specific items (require context)
    sharing_starters = [
        'can you share', 'can you post', 'can you send', 'can you provide',
        'could you share', 'could you post', 'could you send', 'could you provide',
        'would you share', 'would you post', 'would you send',
        'do we skip', 'are we', 'did we', 'should we',
        'which script did you', 'which file did you', 'which command did you',
    ]
    
    if any(phrase in text_lower for phrase in context_phrases):
        return True
    
    if any(text_lower.startswith(starter) for starter in sharing_starters):
        return True
    
    return False


def is_high_quality(candidate: Dict[str, Any], min_answer_words: int = 20) -> bool:
    """Check if candidate meets quality thresholds."""
    answer = candidate.get('proposed_answer', '')
    question = candidate.get('question', '')
    
    # Basic length checks
    if len(question) < 15 or len(answer) < 50:
        return False
    
    # Check for context dependency
    if requires_context(question) or requires_context(answer):
        return False
    
    # Answer should have enough words
    answer_words = len(answer.split())
    if answer_words < min_answer_words:
        return False
    
    # Check for some technical content (URLs, code, technical terms)
    has_url = 'http' in answer or 'www.' in answer
    has_code = '`' in answer or 'python' in answer.lower() or 'import' in answer
    has_commands = any(cmd in answer.lower() for cmd in ['run', 'install', 'configure', 'set', 'create'])
    
    # At least one indicator of technical content
    if not (has_url or has_code or has_commands):
        return False
    
    # Avoid very short answers that look like acknowledgments
    if answer_words < 30 and not (has_url or has_code):
        return False
    
    return True


def deduplicate_exact(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove exact duplicate questions, keeping highest score."""
    question_map = {}
    
    for c in candidates:
        q = c['question']
        score = c.get('score', 0.0)
        
        if q not in question_map or score > question_map[q].get('score', 0.0):
            question_map[q] = c
    
    return list(question_map.values())


def deduplicate_fuzzy(candidates: List[Dict[str, Any]], threshold: float = 0.9) -> List[Dict[str, Any]]:
    """Remove very similar questions using normalized matching."""
    normalized_map = {}
    
    for c in candidates:
        q_norm = normalize_question(c['question'])
        score = c.get('score', 0.0)
        
        # Check if very similar question exists
        found_similar = False
        for existing_norm, existing_c in normalized_map.items():
            # Simple similarity: if normalized strings are very similar
            if q_norm == existing_norm or (len(q_norm) > 20 and q_norm in existing_norm) or (len(existing_norm) > 20 and existing_norm in q_norm):
                # Keep higher scored one
                if score > existing_c.get('score', 0.0):
                    normalized_map[q_norm] = c
                found_similar = True
                break
        
        if not found_similar:
            normalized_map[q_norm] = c
    
    return list(normalized_map.values())


def sample_by_diversity(candidates: List[Dict[str, Any]], 
                        target: int, 
                        group_key: str = 'repo',
                        max_per_group: int = 10) -> List[Dict[str, Any]]:
    """Sample candidates ensuring diversity across groups."""
    # Group by key (repo, channel, etc.)
    groups = defaultdict(list)
    for c in candidates:
        key = c.get(group_key, 'unknown')
        groups[key].append(c)
    
    # Sort each group by score
    for key in groups:
        groups[key].sort(key=lambda x: x.get('score', 0.0), reverse=True)
    
    # Round-robin sampling with limits
    selected = []
    group_counts = defaultdict(int)
    
    # First pass: take up to max_per_group from each group
    for group_name, group_candidates in sorted(groups.items()):
        for c in group_candidates[:max_per_group]:
            if len(selected) >= target:
                break
            selected.append(c)
            group_counts[group_name] += 1
        if len(selected) >= target:
            break
    
    # If we still need more, do a second pass with higher scores
    if len(selected) < target:
        remaining = []
        for group_name, group_candidates in groups.items():
            remaining.extend(group_candidates[max_per_group:])
        
        remaining.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        needed = target - len(selected)
        selected.extend(remaining[:needed])
    
    return selected


def filter_docs(candidates: List[Dict[str, Any]], target: int) -> List[Dict[str, Any]]:
    """Filter documentation candidates."""
    print(f"📄 Filtering documentation candidates (from {len(candidates)} to ~{target})...")
    
    # 1. Deduplicate exact
    candidates = deduplicate_exact(candidates)
    print(f"   After exact dedup: {len(candidates)}")
    
    # 2. Deduplicate fuzzy
    candidates = deduplicate_fuzzy(candidates)
    print(f"   After fuzzy dedup: {len(candidates)}")
    
    # 3. Quality filter
    candidates = [c for c in candidates if is_high_quality(c, min_answer_words=20)]
    print(f"   After quality filter: {len(candidates)}")
    
    # 4. Diversity sampling by repo
    if len(candidates) > target:
        candidates = sample_by_diversity(candidates, target, group_key='repo', max_per_group=8)
        print(f"   After diversity sampling: {len(candidates)}")
    
    # Sort by score
    candidates.sort(key=lambda x: x.get('score', 0.0), reverse=True)
    
    return candidates


def filter_discord(candidates: List[Dict[str, Any]], target: int) -> List[Dict[str, Any]]:
    """Filter Discord candidates."""
    print(f"💬 Filtering Discord candidates (from {len(candidates)} to ~{target})...")
    
    # 1. Deduplicate exact
    candidates = deduplicate_exact(candidates)
    print(f"   After exact dedup: {len(candidates)}")
    
    # 2. Quality filter - stricter for Discord
    candidates = [c for c in candidates if is_high_quality(c, min_answer_words=25)]
    print(f"   After quality filter: {len(candidates)}")
    
    # 3. Remove very short questions/answers
    candidates = [c for c in candidates 
                  if len(c['question']) >= 20 and len(c.get('proposed_answer', '')) >= 80]
    print(f"   After length filter: {len(candidates)}")
    
    # 4. Diversity sampling by channel/category
    if len(candidates) > target:
        # Extract channel from source_file if available
        for c in candidates:
            source = c.get('source_file', '')
            # Extract category from filename like "NOMAD - ab-initio - ..."
            match = re.search(r'NOMAD - ([^-]+) -', source)
            c['category'] = match.group(1).strip() if match else 'general'
        
        candidates = sample_by_diversity(candidates, target, group_key='category', max_per_group=15)
        print(f"   After diversity sampling: {len(candidates)}")
    
    # Sort by score
    candidates.sort(key=lambda x: x.get('score', 0.0), reverse=True)
    
    return candidates


def main():
    parser = argparse.ArgumentParser(description='Filter and deduplicate gold candidates')
    parser.add_argument('--docs-in', type=Path, required=True, help='Input docs JSONL')
    parser.add_argument('--discord-in', type=Path, required=True, help='Input Discord JSONL')
    parser.add_argument('--docs-out', type=Path, required=True, help='Output docs JSONL')
    parser.add_argument('--discord-out', type=Path, required=True, help='Output Discord JSONL')
    parser.add_argument('--target-docs', type=int, default=80, help='Target docs candidates')
    parser.add_argument('--target-discord', type=int, default=120, help='Target Discord candidates')
    parser.add_argument('--write-csv', action='store_true', help='Also write CSV files')
    
    args = parser.parse_args()
    
    print("🎯 Filtering and deduplicating gold candidates\n")
    
    # Load candidates
    docs_candidates = load_jsonl(args.docs_in)
    discord_candidates = load_jsonl(args.discord_in)
    
    print(f"📥 Loaded {len(docs_candidates)} docs + {len(discord_candidates)} Discord = {len(docs_candidates) + len(discord_candidates)} total\n")
    
    # Filter each source
    docs_filtered = filter_docs(docs_candidates, args.target_docs)
    discord_filtered = filter_discord(discord_candidates, args.target_discord)
    
    # Write outputs
    print(f"\n💾 Writing filtered candidates...")
    write_jsonl(docs_filtered, args.docs_out)
    print(f"   ✓ {args.docs_out} ({len(docs_filtered)} candidates)")
    
    write_jsonl(discord_filtered, args.discord_out)
    print(f"   ✓ {args.discord_out} ({len(discord_filtered)} candidates)")
    
    if args.write_csv:
        docs_csv = args.docs_out.with_suffix('.csv')
        discord_csv = args.discord_out.with_suffix('.csv')
        
        write_csv(docs_filtered, docs_csv)
        print(f"   ✓ {docs_csv}")
        
        write_csv(discord_filtered, discord_csv)
        print(f"   ✓ {discord_csv}")
    
    print(f"\n✅ Filtering complete!")
    print(f"   📊 Total filtered: {len(docs_filtered) + len(discord_filtered)} candidates")
    print(f"      • Documentation: {len(docs_filtered)}")
    print(f"      • Discord: {len(discord_filtered)}")
    print(f"   📉 Reduction: {len(docs_candidates) + len(discord_candidates)} → {len(docs_filtered) + len(discord_filtered)} ({100 * (1 - (len(docs_filtered) + len(discord_filtered)) / (len(docs_candidates) + len(discord_candidates))):.1f}% reduction)")


if __name__ == '__main__':
    main()
