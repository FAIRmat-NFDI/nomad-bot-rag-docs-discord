#!/usr/bin/env python3
"""
Harvest high-quality Q&A from Discord by analyzing conversation threads.

This approach:
1. Groups messages by time gaps to identify conversation threads
2. Detects technical questions within threads
3. Aggregates all relevant responses (not just immediate reply)
4. Strips greetings, acknowledgments, and conversational noise
5. Synthesizes clean, technical Q&A pairs

Usage:
    uv run python utils/gold/harvest_discord_conversations.py \
        --raw-glob "/path/to/discord/*.json" \
        --out-jsonl data/evaluation/gold_candidates_discord_conversations.jsonl \
        --out-csv data/evaluation/gold_candidates_discord_conversations.csv \
        --write-csv \
        --time-gap-minutes 30 \
        --min-thread-messages 3 \
        --max-candidates 200
"""

import argparse
import json
import csv
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib


# === Content Cleaning ===

NOISE_PATTERNS = [
    r'^(hi|hey|hello|thanks|thank you|thx|cheers|great|awesome|perfect|cool|nice|ok|okay|got it|sure|np|no problem)[,!\s]*$',
    r'^@\w+\s*(hi|hey|hello|thanks)',  # Greetings with mentions
    r'^\s*:\w+:\s*$',  # Emoji-only messages
    r'^(yes|no|yep|nope|yeah|nah)\s*[.!]*$',  # Simple yes/no
]

GREETING_STARTS = [
    'hi ', 'hey ', 'hello ', 'thanks ', 'thank you', 'cheers',
    'good morning', 'good afternoon', 'good evening',
]

ACKNOWLEDGMENT_PHRASES = [
    'thanks for', 'thank you for', 'got it', 'makes sense',
    'i see', 'understood', 'appreciate it', 'will do',
]

URL_PATTERN = re.compile(r'https?://\S+')
CODE_BLOCK_PATTERN = re.compile(r'```[\s\S]+?```')
INLINE_CODE_PATTERN = re.compile(r'`[^`]+`')
MENTION_PATTERN = re.compile(r'@\w+')


def is_noise(text: str) -> bool:
    """Check if message is just noise (greetings, acknowledgments, etc.)"""
    text_clean = text.strip().lower()
    
    if len(text_clean) < 10:
        for pattern in NOISE_PATTERNS:
            if re.match(pattern, text_clean, re.IGNORECASE):
                return True
    
    # Check if starts with common greetings
    for greeting in GREETING_STARTS:
        if text_clean.startswith(greeting):
            # If it's ONLY a greeting, it's noise
            rest = text_clean[len(greeting):].strip()
            if len(rest) < 20:
                return True
    
    # Check for pure acknowledgments
    for ack in ACKNOWLEDGMENT_PHRASES:
        if ack in text_clean and len(text_clean) < 50:
            return True
    
    return False


def clean_message(text: str) -> str:
    """Clean message text - remove greetings, strip mentions at start, normalize whitespace"""
    text = text.strip()
    
    # Remove leading greetings
    for greeting in GREETING_STARTS:
        if text.lower().startswith(greeting):
            text = text[len(greeting):].strip()
            # Remove following punctuation
            text = re.sub(r'^[,!\s]+', '', text)
    
    # Remove standalone acknowledgments at start
    for ack in ACKNOWLEDGMENT_PHRASES:
        if text.lower().startswith(ack):
            text = text[len(ack):].strip()
            text = re.sub(r'^[,!\s]+', '', text)
    
    # Remove leading mentions (but keep inline ones for context)
    text = re.sub(r'^(@\w+\s*)+', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def has_technical_content(text: str) -> bool:
    """Check if text has substantive technical content"""
    # Check length
    if len(text) < 30:
        return False
    
    # Check for technical indicators
    has_code = bool(CODE_BLOCK_PATTERN.search(text) or INLINE_CODE_PATTERN.search(text))
    has_url = bool(URL_PATTERN.search(text))
    
    # Technical terms
    tech_terms = [
        'error', 'install', 'run', 'config', 'file', 'code', 'function',
        'class', 'import', 'package', 'version', 'dependency', 'api',
        'schema', 'parser', 'plugin', 'nomad', 'docker', 'python',
        'git', 'branch', 'merge', 'commit', 'repository',
    ]
    
    text_lower = text.lower()
    has_tech_terms = sum(1 for term in tech_terms if term in text_lower) >= 2
    
    return has_code or has_url or has_tech_terms


def extract_question(text: str) -> Optional[str]:
    """Extract the core question from text, or return None if not a question"""
    text = clean_message(text)
    
    if not text:
        return None
    
    # Must have question indicators
    has_question_mark = '?' in text
    question_words = ['how', 'what', 'why', 'when', 'where', 'which', 'who', 'can', 'could', 'should', 'would', 'is', 'are', 'does', 'do', 'did']
    has_question_word = any(text.lower().startswith(qw + ' ') or f' {qw} ' in text.lower() for qw in question_words)
    
    if not (has_question_mark or has_question_word):
        return None
    
    # Split into sentences, find question sentences
    sentences = re.split(r'[.!]\s+', text)
    questions = []
    
    for sent in sentences:
        sent = sent.strip()
        if '?' in sent or any(sent.lower().startswith(qw + ' ') for qw in question_words):
            if len(sent) > 20 and has_technical_content(sent):
                questions.append(sent)
    
    if questions:
        # Return first substantial question
        return questions[0] if not questions[0].endswith('?') else questions[0]
    
    # If no clear question sentence but has question mark and technical content
    if has_question_mark and has_technical_content(text):
        # Return the part up to first question mark
        first_q = text.split('?')[0] + '?'
        if len(first_q) > 20:
            return first_q
    
    return None


# === Thread Analysis ===

def parse_timestamp(ts_str: str) -> datetime:
    """Parse Discord timestamp to datetime"""
    # Format: "2024-02-20T11:28:19.172+01:00"
    # Try with timezone first, fall back to naive
    for fmt in ["%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]:
        try:
            return datetime.strptime(ts_str.split('+')[0].split('Z')[0], fmt.replace('%z', ''))
        except:
            continue
    return datetime.now()


def load_discord_export(json_path: Path) -> List[Dict[str, Any]]:
    """Load Discord export JSON and extract messages"""
    with json_path.open() as f:
        data = json.load(f)
    
    messages = []
    for msg in data.get('messages', []):
        # Skip bot messages and system messages
        if msg.get('author', {}).get('isBot', False):
            continue
        if msg.get('type') != 'Default' and msg.get('type') != '21':  # 21 is thread message
            continue
        
        content = msg.get('content', '').strip()
        if not content or len(content) < 10:
            continue
        
        messages.append({
            'id': msg['id'],
            'author': msg.get('author', {}).get('name', 'unknown'),
            'content': content,
            'timestamp': parse_timestamp(msg['timestamp']),
            'raw': msg,
        })
    
    return sorted(messages, key=lambda m: m['timestamp'])


def segment_into_threads(messages: List[Dict], time_gap_minutes: int = 30) -> List[List[Dict]]:
    """Segment messages into conversation threads based on time gaps"""
    if not messages:
        return []
    
    threads = []
    current_thread = [messages[0]]
    
    for msg in messages[1:]:
        time_gap = (msg['timestamp'] - current_thread[-1]['timestamp']).total_seconds() / 60
        
        if time_gap > time_gap_minutes:
            # Start new thread
            if len(current_thread) >= 2:  # Only keep threads with multiple messages
                threads.append(current_thread)
            current_thread = [msg]
        else:
            current_thread.append(msg)
    
    # Add last thread
    if len(current_thread) >= 2:
        threads.append(current_thread)
    
    return threads


def analyze_thread(thread: List[Dict], min_messages: int = 3) -> Optional[Dict[str, Any]]:
    """Analyze a thread to extract Q&A pair"""
    if len(thread) < min_messages:
        return None
    
    # Find the question
    question_msg = None
    question_idx = None
    
    for idx, msg in enumerate(thread):
        q = extract_question(msg['content'])
        if q:
            question_msg = msg
            question_idx = idx
            break
    
    if not question_msg:
        return None
    
    # Collect response messages (after question, from different authors)
    responses = []
    question_author = question_msg['author']
    
    for msg in thread[question_idx + 1:]:
        # Skip messages from question author (clarifications)
        if msg['author'] == question_author:
            continue
        
        # Skip noise
        if is_noise(msg['content']):
            continue
        
        # Clean and add
        cleaned = clean_message(msg['content'])
        if cleaned and has_technical_content(cleaned):
            responses.append(cleaned)
    
    if not responses:
        return None
    
    # Synthesize answer from responses
    # Take first substantial response (usually the main answer)
    # If there are follow-ups with additional info, append them
    answer_parts = []
    
    # Main answer (first response)
    answer_parts.append(responses[0])
    
    # Add follow-ups if they add new information (not just acknowledgments)
    for resp in responses[1:3]:  # Max 2 follow-ups
        if len(resp) > 50 and not any(resp.startswith(ack) for ack in ACKNOWLEDGMENT_PHRASES):
            answer_parts.append(resp)
    
    answer = ' '.join(answer_parts)
    
    # Final quality check
    if len(answer) < 50 or not has_technical_content(answer):
        return None
    
    return {
        'question': extract_question(question_msg['content']),
        'answer': answer,
        'thread_length': len(thread),
        'response_count': len(responses),
        'source_file': thread[0].get('source_file', ''),
        'thread_start': thread[0]['timestamp'].isoformat(),
    }


# === Main Processing ===

def score_qa_pair(qa: Dict[str, Any]) -> float:
    """Score a Q&A pair for quality"""
    score = 0.5  # Base score
    
    question = qa['question']
    answer = qa['answer']
    
    # Question quality
    if '?' in question:
        score += 0.1
    if len(question.split()) >= 8:
        score += 0.1
    
    # Answer quality
    answer_words = len(answer.split())
    if 30 <= answer_words <= 500:
        score += 0.2
    
    if CODE_BLOCK_PATTERN.search(answer):
        score += 0.15
    if URL_PATTERN.search(answer):
        score += 0.1
    if INLINE_CODE_PATTERN.search(answer):
        score += 0.05
    
    # Thread quality
    if qa['thread_length'] >= 5:
        score += 0.1
    if qa['response_count'] >= 2:
        score += 0.05
    
    return min(score, 1.0)


def process_discord_exports(glob_pattern: str, 
                            time_gap_minutes: int,
                            min_thread_messages: int,
                            max_candidates: int) -> List[Dict[str, Any]]:
    """Process all Discord export files"""
    import glob as glob_module
    
    files = glob_module.glob(glob_pattern, recursive=True)
    print(f"📁 Found {len(files)} Discord export files")
    
    all_candidates = []
    seen_questions = set()
    
    for file_path in files:
        path = Path(file_path)
        print(f"   Processing {path.name}...")
        
        try:
            messages = load_discord_export(path)
            if not messages:
                continue
            
            # Add source file to messages
            for msg in messages:
                msg['source_file'] = path.name
            
            threads = segment_into_threads(messages, time_gap_minutes)
            print(f"      Found {len(threads)} conversation threads")
            
            for thread in threads:
                qa = analyze_thread(thread, min_thread_messages)
                if qa:
                    # Deduplicate by question
                    q_hash = hashlib.md5(qa['question'].lower().encode()).hexdigest()[:16]
                    if q_hash in seen_questions:
                        continue
                    seen_questions.add(q_hash)
                    
                    # Score and add
                    qa['score'] = score_qa_pair(qa)
                    qa['id'] = f"discord-conv-{q_hash}"
                    all_candidates.append(qa)
        
        except Exception as e:
            print(f"      ⚠️  Error processing {path.name}: {e}")
            continue
    
    # Sort by score and limit
    all_candidates.sort(key=lambda x: x['score'], reverse=True)
    
    if len(all_candidates) > max_candidates:
        all_candidates = all_candidates[:max_candidates]
    
    print(f"\n✅ Extracted {len(all_candidates)} high-quality Q&A pairs")
    return all_candidates


def write_output(candidates: List[Dict[str, Any]], jsonl_path: Path, csv_path: Optional[Path] = None):
    """Write candidates to JSONL and optionally CSV"""
    # Write JSONL
    with jsonl_path.open('w') as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')
    
    print(f"📄 Wrote {len(candidates)} candidates to {jsonl_path}")
    
    # Write CSV
    if csv_path:
        with csv_path.open('w', newline='', encoding='utf-8') as f:
            if candidates:
                writer = csv.DictWriter(f, fieldnames=candidates[0].keys())
                writer.writeheader()
                writer.writerows(candidates)
        print(f"📄 Wrote CSV to {csv_path}")


def main():
    parser = argparse.ArgumentParser(description='Harvest Discord conversations into Q&A pairs')
    parser.add_argument('--raw-glob', required=True, help='Glob pattern for Discord JSON files')
    parser.add_argument('--out-jsonl', type=Path, required=True, help='Output JSONL file')
    parser.add_argument('--out-csv', type=Path, help='Output CSV file')
    parser.add_argument('--write-csv', action='store_true', help='Write CSV output')
    parser.add_argument('--time-gap-minutes', type=int, default=30, help='Time gap to split threads (minutes)')
    parser.add_argument('--min-thread-messages', type=int, default=3, help='Min messages per thread')
    parser.add_argument('--max-candidates', type=int, default=200, help='Max candidates to output')
    
    args = parser.parse_args()
    
    print("🎯 Harvesting Discord conversations\n")
    
    candidates = process_discord_exports(
        args.raw_glob,
        args.time_gap_minutes,
        args.min_thread_messages,
        args.max_candidates
    )
    
    csv_path = args.out_csv if args.write_csv else None
    write_output(candidates, args.out_jsonl, csv_path)
    
    print(f"\n✅ Done! Generated {len(candidates)} Q&A candidates")


if __name__ == '__main__':
    main()
