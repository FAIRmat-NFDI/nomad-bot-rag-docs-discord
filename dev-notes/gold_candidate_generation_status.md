# Gold Candidate Generation - Project Status & Documentation

**Date:** December 17, 2025
**Project:** NOMAD RAG Chatbot Evaluation Dataset Expansion
**Branch:** `extend-gold-eval-set`

---

## Project Overview

### Objective
Expand the `gold_all.jsonl` evaluation dataset by ~200 high-quality Q&A candidates for testing the NOMAD RAG chatbot. These candidates must be:
- Technically substantive
- Self-contained (no contextual dependencies)
- Representative of real user questions
- Manually reviewed and approved before inclusion

### Current Gold Dataset
- **Location:** `data/evaluation/gold_all.jsonl`
- **Current Size:** 105 entries
- **Content:** Mix of NOMAD glossary terms and Discord issue Q&As
- **Target:** Add ~200 new candidates (total ~305)

### Data Sources

#### 1. Documentation Repositories
**Location:** `data/fetched/`
**Total Files:** 1,267 markdown files
**Repositories:** 46+ GitHub repositories

<details>
<summary>Complete Repository List (click to expand)</summary>

```
AreaA-data_modeling_and_schemas/
AreaC-Tutorial-CECAM-2023/
AreaC-Tutorial10_2023/
fairmat-tutorial-14-computational-plugins/
FAIRmat-tutorial-16/
nomad-aitoolkit/
nomad-analysis/
nomad-api/
nomad-auto-xrd/
nomad-bayesian-optimization/
nomad-camels-plugin/
nomad-catalysis-plugin/
nomad-crystallm/
nomad-docs/
nomad-lab-homepage/
nomad-material-processing/
nomad-material-processing-example/
nomad-measurements/
nomad-neb-workflows/
nomad-parser-edmft/
nomad-parser-fhiaims/
nomad-parser-vasp/
nomad-parser-wannier90/
nomad-porous-materials/
nomad-remote-tools-hub/
nomad-schema-plugin-example/
nomad-simulations/
nomad-utility-workflows/
pynxtools/
pynxtools-apm/
pynxtools-em/
pynxtools-ellips/
pynxtools-mpes/
pynxtools-raman/
pynxtools-stm/
pynxtools-xps/
pynxtools-xrd/
workflow-parsers/
nomad-onboarding-workshop/
```
</details>

**Content Types:**
- README.md files
- Documentation pages
- Tutorial notebooks
- How-to guides
- API documentation

#### 2. Discord Chat Exports
**Primary Location:** `/home/jfrudzinski/work/Discord/Analytics/nomad_discord_Q*_202*/`
**Export Format:** DiscordChatExporter JSON
**Total Threads:** ~989 conversation threads
**Time Period:** Q1 2024 - Q3 2025

**Export File Pattern:**
```
nomad_discord_Q1_2024/*.json
nomad_discord_Q2_2024/*.json
nomad_discord_Q3_2024/*.json
nomad_discord_Q4_2024/*.json
nomad_discord_Q1_2025/*.json
nomad_discord_Q2_2025/*.json
nomad_discord_Q3_2025/*.json
```

**Channel Categories:**
- `#issues` - Bug reports and issue discussions
- `#discussion` - General technical discussions
- `#area-b-devs` - Development area B
- `#area-c-fairmat-internal` - FAIRmat internal discussions
- `#oasis` - OASIS project discussions
- `#a-team-internal` - A-team internal channel
- `#data-schema-updates` - Schema update discussions
- `#taskforce-plugins` - Plugin development task force
- `#measurements` - Measurement-related discussions
- And more...

**Export Command Used:**
```bash
DiscordChatExporter.Cli exportguild \
    --token <TOKEN> \
    --guild <NOMAD_GUILD_ID> \
    --output "/home/jfrudzinski/work/Discord/Analytics/nomad_discord_Q*_202*/" \
    --format json \
    --dateformat "yyyy-MM-dd'T'HH:mm:sszzz"
```

---

## Current Status Summary

### Phase 1: Initial Candidate Generation ✅ COMPLETED
- Generated 1,483 total candidates
  - Documentation: 88 candidates
  - Discord (simple extraction): 1,395 candidates
- **Issue Identified:** Quality problems with simple Q&A extraction
  - Context-dependent questions ("above", "as discussed")
  - Conversational noise (greetings, acknowledgments)
  - Immediate-reply-only approach missing full context

### Phase 2: Filtering & Quality Improvement ✅ COMPLETED
- Applied filters to reduce to 148 candidates
  - Removed exact duplicates
  - Removed context-dependent questions
  - Applied quality thresholds (length, technical content)
- **Issue Identified:** Still too many low-quality candidates
  - Questions like "Can you share/post..."
  - Conversational fragments without full technical context
  - User feedback: "too chatty", needs better Q&A synthesis

### Phase 3: Conversation-Based Harvesting ✅ COMPLETED
- Developed sophisticated conversation analysis approach
- Generated 200 high-quality candidates using thread-aware extraction
- **Current State:** Ready for manual review

### Phase 4: Manual Review 🔄 IN PROGRESS
- Approved candidates so far:
  - **Old batch, Candidate 3:** Discord restore process Q&A
  - **Old batch, Candidate 19:** Downloading NOMAD data Q&A (needs greeting removal)
- User requested alternative approach due to review fatigue

---

## Tools Developed

### 1. `utils/gold/generate_gold_candidates.py`
**Purpose:** Initial dual-source candidate generation
**Status:** ✅ Working but superseded by conversation-based approach

**Features:**
- Extracts Q&As from markdown documentation
- Parses Discord JSONL exports (simple approach)
- Scoring heuristics (0-1 scale)
- Per-repo limits for diversity
- Outputs JSONL + CSV

**Usage:**
```bash
uv run python utils/gold/generate_gold_candidates.py \
    --batch 2025-12-17 \
    --docs-target 100 \
    --discord-target 100
```

**Key Functions:**
- `extract_from_readme()`: Heading-based Q&A extraction from markdown
- `extract_discord_qa()`: Simple question/answer pattern matching
- `score_candidate()`: Heuristic quality scoring
- `harvest_documentation()`: Process all markdown files
- `harvest_discord()`: Process Discord exports

**Limitations:**
- Discord extraction too simplistic (immediate reply only)
- No conversation context awareness
- Produces chatty, incomplete answers

---

### 2. `utils/gold/filter_and_deduplicate_candidates.py`
**Purpose:** Quality filtering and deduplication
**Status:** ✅ Working, used for Phase 2

**Features:**
- Exact question deduplication
- Fuzzy question matching (normalized text)
- Context-dependency detection (40+ phrases)
- Quality filters (length, technical content, etc.)
- Diversity sampling (limits per repo/category)

**Usage:**
```bash
uv run python utils/gold/filter_and_deduplicate_candidates.py \
    --docs-in data/evaluation/gold_candidates_docs_2025-12-17.jsonl \
    --discord-in data/evaluation/gold_candidates_discord_2025-12-17.jsonl \
    --docs-out data/evaluation/gold_candidates_docs_filtered_2025-12-17.jsonl \
    --discord-out data/evaluation/gold_candidates_discord_filtered_2025-12-17.jsonl \
    --target-docs 80 \
    --target-discord 120 \
    --write-csv
```

**Key Functions:**
- `requires_context()`: Detects context-dependent questions
  - Phrases: "above", "below", "as discussed", "corresponding", etc.
  - Request patterns: "can you share", "can you post", etc.
- `is_high_quality()`: Multi-criteria quality check
  - Length requirements
  - Technical content detection (URLs, code, commands)
  - Noise filtering (acknowledgments, greetings)
- `deduplicate_exact()`: Remove identical questions
- `deduplicate_fuzzy()`: Remove very similar questions
- `sample_by_diversity()`: Ensure representation across sources

**Context Filters (40+ patterns):**
```python
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

sharing_starters = [
    'can you share', 'can you post', 'can you send', 'can you provide',
    'could you share', 'could you post', 'could you send', 'could you provide',
    'would you share', 'would you post', 'would you send',
    'do we skip', 'are we', 'did we', 'should we',
    'which script did you', 'which file did you', 'which command did you',
]
```

**Results:**
- Input: 1,483 candidates
- Output: 148 candidates (90% reduction)

---

### 3. `utils/gold/harvest_discord_conversations.py` ⭐ RECOMMENDED
**Purpose:** Sophisticated conversation-aware Q&A extraction  
**Status:** ✅ Working, best quality results

**Features:**
- **Thread Segmentation:** Groups messages by time gaps (default 30 min)
- **Conversation Analysis:** Understands multi-message exchanges
- **Intelligent Synthesis:** Combines multiple responses into coherent answers
- **Aggressive Cleaning:** Removes greetings, acknowledgments, mentions
- **Context Awareness:** Filters self-referential content
- **Quality Scoring:** Technical content detection, length optimization

**Usage:**
```bash
uv run python utils/gold/harvest_discord_conversations.py \
    --raw-glob "/home/jfrudzinski/work/Discord/Analytics/nomad_discord_Q*_202*/*.json" \
    --out-jsonl data/evaluation/gold_candidates_discord_conversations.jsonl \
    --out-csv data/evaluation/gold_candidates_discord_conversations.csv \
    --write-csv \
    --time-gap-minutes 30 \
    --min-thread-messages 3 \
    --max-candidates 200
```

**Architecture:**

1. **Message Loading & Filtering:**
   - Parse DiscordChatExporter JSON
   - Skip bot messages and system messages
   - Extract author, content, timestamp

2. **Thread Segmentation:**
   - Group messages by time gaps
   - Identify conversation boundaries
   - Minimum 2-3 messages per thread

3. **Question Detection:**
   - Pattern matching (20+ question indicators)
   - Technical content requirements
   - Length thresholds (20+ chars)

4. **Answer Synthesis:**
   - Collect responses from different authors
   - Skip question author's follow-ups
   - Remove noise (greetings, acks)
   - Combine main answer + substantial follow-ups

5. **Content Cleaning:**
   ```python
   # Removes:
   - Leading greetings ("hi", "hey", "hello", "thanks")
   - Acknowledgments ("got it", "makes sense")
   - Leading mentions (@username)
   - Emoji-only messages
   - Simple yes/no responses
   ```

6. **Quality Scoring:**
   ```python
   score = 0.5  # base
   + 0.1  # has question mark
   + 0.1  # question ≥8 words
   + 0.2  # answer 30-500 words
   + 0.15 # has code block
   + 0.1  # has URL
   + 0.05 # has inline code
   + 0.1  # thread length ≥5
   + 0.05 # multiple responses
   ```

**Key Functions:**
- `is_noise()`: Detect non-technical chat noise
- `clean_message()`: Remove greetings, mentions, normalize whitespace
- `has_technical_content()`: Verify substantive technical content
- `extract_question()`: Find and clean core question
- `segment_into_threads()`: Time-based conversation grouping
- `analyze_thread()`: Extract Q&A from conversation context
- `score_qa_pair()`: Multi-factor quality assessment

**Output Schema:**
```json
{
  "id": "discord-conv-<hash>",
  "question": "How do I implement child_archives?",
  "answer": "The child archives can be generated...",
  "thread_length": 8,
  "response_count": 3,
  "source_file": "NOMAD - discussion - ....json",
  "thread_start": "2024-02-20T11:28:19",
  "score": 0.85
}
```

**Results:**
- Input: 989 Discord conversation threads
- Output: 200 high-quality candidates
- Average score: 0.75+

---

### 4. `utils/gold/harvest_gold_from_html.py`
**Purpose:** Harvest Q&A-style pairs from static documentation sites (MkDocs / tutorials)  
**Status:** ✅ Used for NOMAD onboarding workshop scrape

**Features:**
- Parses mirrored HTML snapshots and splits content by headings
- Detects FAQ-style `<details>`/`dl` blocks and inline questions in paragraphs
- Generates fallback questions from "How to ..." headings
- Scores candidates (0-1) based on structure, length, and technical signals

**Usage (Workshop example):**
```bash
uv run python utils/gold/harvest_gold_from_html.py \
    --html-root data/fetched/nomad-onboarding-workshop/html/nomad-onboarding-workshop \
    --base-url https://fairmat-nfdi.github.io/nomad-onboarding-workshop \
    --min-score 0.55 \
    --write-csv
```

**Results (Workshop scrape):**
- HTML snapshot mirrored to `data/fetched/nomad-onboarding-workshop/html/`
- Raw pairs detected: 47
- Kept (score ≥0.55 and question-like): 35
- Output: `data/evaluation/gold_candidates_nomad_onboarding_workshop.*`

---

### 5. `utils/gold/harvest_gold_from_markdown.py`
**Purpose:** Batch-harvest question/answer candidates from Markdown-based documentation repos  
**Status:** ✅ Ran across all repos in `data/documentation_links.txt`

**Features:**
- Walks `data/fetched/**` and splits Markdown into sections
- Detects heading questions, FAQ blocks, and inline question sentences
- Skips boilerplate phrases (e.g., "what you will learn", "how to use this plugin") to avoid low-signal entries
- Drops duplicate questions globally, keeping the highest-scoring instance
- Scores candidates (0-1) based on question form, answer length, and technical cues
- Emits JSONL + optional CSV for manual review

**Usage (current sweep):**
```bash
uv run python utils/gold/harvest_gold_from_markdown.py \
    --md-root data/fetched \
    --base-url-template https://github.com/FAIRmat-NFDI/{repo}/blob/main/{path} \
    --min-score 0.55 \
    --max-candidates 500 \
    --write-csv
```

**Results (2025-12-17 sweep):**
- Markdown files scanned: 689 across 47 repos (cloned via `data/documentation_links.txt`)
- Raw Q&A candidates detected: 436
- Kept (score ≥0.55): 429
- Outputs: `data/evaluation/gold_candidates_docs_2025.jsonl` + `.csv`

---

### 6. `utils/gold/harvest_discord_issues.py`
**Purpose:** Summarize Discord “issues” threads into concise Q&A pairs  
**Status:** ✅ New tool focused on #issues threads with thread-aware summarization

**Features:**
- Loads DiscordChatExporter JSON, only keeps channels whose category is `issues`
- Treats each thread as a single Q&A, combining the reporter’s initial message(s) into a question
- Summarizes maintainer responses to form a narrative answer (not verbatim snippets) and strips user names for privacy
- Deduplicates across threads and tags each candidate with message/author metadata

**Usage:**
```bash
uv run python utils/gold/harvest_discord_issues.py \
    --issues-glob "/home/jfrudzinski/work/Discord/Analytics/nomad_discord_Q*_202*/NOMAD - issues - *.json" \
    --out-jsonl data/evaluation/gold_candidates_discord_issues.jsonl \
    --out-csv data/evaluation/gold_candidates_discord_issues.csv \
    --write-csv
```

**Results:**
- Issue threads processed: ~160 (all exports matching glob)
- Summarized candidates: 166
- Output artifacts:
  - `data/evaluation/gold_candidates_discord_issues.jsonl` / `.csv` – structured data for tooling
  - `data/evaluation/gold_candidates_discord_issues_review.md` – reviewer-friendly Markdown that lists each Q&A with checkboxes (`[ ] Accept / [ ] Reject`) so decisions can be made directly in the file; this Markdown is parsed later to ingest edits and approvals back into `gold_all.jsonl`

---

## Generated Data Files

### Current Candidate Files

#### Phase 2 Outputs (Filtered - Lower Quality)
1. **`data/evaluation/gold_candidates_docs_filtered_2025-12-17.jsonl`**
   - 28 documentation candidates
   - Filtered from 88 original

2. **`data/evaluation/gold_candidates_discord_filtered_2025-12-17.jsonl`**
   - 120 Discord candidates
   - Filtered from 1,395 original
   - Simple extraction approach

3. **CSV versions:** `.csv` files for spreadsheet review

#### Phase 3 Outputs (Conversation-based - High Quality) ⭐
1. **`data/evaluation/gold_candidates_discord_conversations.jsonl`** 
   - 200 conversation-analyzed candidates
   - Best quality, ready for review

2. **`data/evaluation/gold_candidates_discord_conversations.csv`**
   - Same as above, spreadsheet format

#### NOMAD Onboarding Workshop Outputs (Documentation - Newly Added)
1. **`data/evaluation/gold_candidates_nomad_onboarding_workshop.jsonl`**
   - 35 high-confidence candidates harvested from https://fairmat-nfdi.github.io/nomad-onboarding-workshop/
   - Derived via the `utils/gold/harvest_gold_from_html.py` scraper on the mirrored HTML snapshot

2. **`data/evaluation/gold_candidates_nomad_onboarding_workshop.csv`**
   - Same candidates for spreadsheet review
   - Contains `keep` column for triage plus source URLs back to the workshop pages

#### Markdown Documentation Harvest (2025-12-17)
1. **`data/evaluation/gold_candidates_docs_2025.jsonl`**
   - 429 Markdown-derived candidates from 47 documentation repos (`data/documentation_links.txt`)
   - Uses `harvest_gold_from_markdown.py` (see Tool #5) with score ≥0.55 and cap 500

2. **`data/evaluation/gold_candidates_docs_2025.csv`**
   - Spreadsheet review companion with `keep` column + source URLs

#### Discord Issue Thread Summaries (2025-12-17)
1. **`data/evaluation/gold_candidates_discord_issues.jsonl`**
   - 166 summarized Q&A pairs generated by `harvest_discord_issues.py`
   - One record per issue thread; question and answer synthesized from full conversation context

2. **`data/evaluation/gold_candidates_discord_issues.csv`**
   - Spreadsheet version with thread title, message counts, and scores for triage (no personal identifiers)

3. **`data/evaluation/gold_candidates_discord_issues_review.md`**
   - Markdown review sheet containing the same Q&A pairs without metadata noise
   - Each entry includes checkboxes to mark `[x] Accept` or `[x] Reject`; this file preserves reviewer edits to the Q&A text so approved versions can be copied verbatim into `gold_all.jsonl`

### Unfiltered Original Files
- `gold_candidates_docs_2025-12-17.jsonl` (88 docs)
- `gold_candidates_discord_2025-12-17.jsonl` (1,395 Discord)

---

## Manual Review Process

### Original Plan (User Rejected)
1. Review 5 candidates at a time in terminal
2. Respond with yes/no for each
3. Agent copies approved candidates to `gold_all.jsonl`

**Status:** User experienced review fatigue after ~25 candidates

### Approved Candidates (So Far)
Only 2 candidates approved from old batch:

**Candidate 3 (Old Batch):**
```
Q: is there a docker container which makes it possible to run the nomad
   python package on client side on windows? A user of mine deleted all
   of his uploads. I have backups including mongo dumps elastic etc.
   what is the best way to restore a selected set of uploads?

A: Sorry for the late reply... [explains mongorestore process and file
   restoration]
```

**Candidate 19 (Old Batch - needs edit):**
```
Q: What is the simplest way to download all of the data from NOMAD
   (sync it locally) such that one can do simple things such as making
   a Venn-diagram of all of the different classes of materials?

A: Thanks for posting, any questions are welcome 😁 You can make an API
   call to query the NOMAD repository... (there are 112 TBs of data!)

NOTE: Remove "Hi @chaxor !" from answer
```

---

## Recommended Next Steps

### Option 1: Alternative Review Approach
- Use spreadsheet software (Excel/LibreOffice) for batch review
- Add "approved" column to CSV files
- Filter and process approved rows

### Option 2: Automated Quality Tiers
- Implement strict automatic approval for score ≥ 0.85
- Manual review only for 0.70-0.84 range
- Auto-reject below 0.70

### Option 3: Sampling Strategy
- Review 20-30 candidates manually
- Use approved examples to train quality model
- Auto-select similar candidates

### Option 4: Hybrid Approach
- Auto-approve top 50 highest-scoring conversation candidates (score ≥ 0.85)
- Manual review middle 100 (score 0.70-0.84)
- Skip bottom 50
- Supplement with top documentation candidates

---

## Technical Architecture

### Environment
- **Python:** 3.10.12
- **Package Manager:** uv
- **Dependencies:** 168 packages including:
  - chromadb==1.0.20
  - fastapi==0.116.1
  - gradio==5.41.0
  - sentence-transformers==5.1.0
  - torch==2.8.0
  - transformers==4.56.1

### File Structure
```
nomad-bot-rag-docs-discord/
├── data/
│   ├── evaluation/
│   │   ├── gold_all.jsonl                    # Main gold dataset (105)
│   │   ├── gold_candidates_docs_2025-12-17.* # Phase 1 docs (88)
│   │   ├── gold_candidates_discord_2025-12-17.* # Phase 1 Discord (1395)
│   │   ├── gold_candidates_docs_filtered_2025-12-17.* # Phase 2 docs (28)
│   │   ├── gold_candidates_discord_filtered_2025-12-17.* # Phase 2 Discord (120)
│   │   ├── gold_candidates_discord_conversations.* # Phase 3 (200) ⭐
│   │   └── gold_candidates_nomad_onboarding_workshop.* # Workshop docs (35)
│   └── fetched/                              # Markdown docs (1267 files)
├── utils/
│   └── gold/
│       ├── generate_gold_candidates.py       # Phase 1 tool
│       ├── filter_and_deduplicate_candidates.py # Phase 2 tool
│       └── harvest_discord_conversations.py  # Phase 3 tool ⭐
└── docs/
    └── gold_candidate_generation_status.md   # This file
```

### Discord Export Format
```json
{
  "guild": {"id": "...", "name": "NOMAD"},
  "channel": {"id": "...", "name": "...", "category": "..."},
  "messages": [
    {
      "id": "...",
      "timestamp": "2024-02-20T11:28:19.172+01:00",
      "author": {"name": "...", "isBot": false},
      "content": "..."
    }
  ]
}
```

---

## Known Issues & Limitations

### 1. Context Dependencies
**Problem:** Some questions reference previous messages
**Solution:** Implemented 40+ context phrase filters
**Remaining:** Some edge cases may slip through

### 2. Conversation Noise
**Problem:** Greetings, acknowledgments, off-topic chat
**Solution:** Aggressive cleaning in conversation harvester
**Quality:** Significant improvement in Phase 3

### 3. Answer Synthesis
**Problem:** Multi-message answers need combination
**Solution:** Thread-aware synthesis (main + follow-ups)
**Limitation:** Max 3 response blocks to avoid bloat

### 4. Technical Specificity
**Problem:** Some answers too general or vague
**Solution:** Technical content scoring requirements
**Trade-off:** May exclude some valid beginner questions

### 5. Manual Review Bottleneck
**Problem:** 200 candidates too many for manual review
**Status:** User requested alternative approach
**Next:** Need automated or sampling strategy

---

## Quality Metrics

### Conversation-Based Harvester (Phase 3)
- **Candidate Quality:** High (score-based filtering)
- **Self-containment:** Good (context filters applied)
- **Technical Depth:** Excellent (multi-message synthesis)
- **Diversity:** Good (989 threads → 200 candidates)
- **Manual Review:** 0/200 completed

### Simple Filtered Approach (Phase 2)
- **Candidate Quality:** Medium-Low
- **User Feedback:** "too chatty", "not great"
- **Manual Review:** 2/148 approved (1.4%)
- **Status:** Superseded by Phase 3

---

## Code Quality & Maintainability

### Documentation
- ✅ Comprehensive docstrings
- ✅ Usage examples in headers
- ✅ Type hints (partial)
- ✅ Inline comments for complex logic

### Error Handling
- ✅ Try-except blocks for file operations
- ✅ Graceful degradation (skip bad files)
- ✅ Progress logging
- ⚠️ Limited input validation

### Testing
- ⚠️ No unit tests
- ✅ Manual validation on full dataset
- ✅ Output format verification

### Performance
- ✅ Efficient file processing
- ✅ Incremental output writing
- ⚠️ No parallel processing (not needed)

---

## Future Improvements

### Short-term
1. Implement automated approval for high-scoring candidates
2. Create merge script for approved candidates → gold_all.jsonl
3. Add quality report generation

### Medium-term
1. Add unit tests for core functions
2. Implement ML-based quality prediction
3. Create web UI for review process

### Long-term
1. Real-time Discord integration
2. Continuous candidate generation pipeline
3. A/B testing framework for RAG evaluation

---

## Contact & Handoff

### Key Files to Review
1. `utils/gold/harvest_discord_conversations.py` - Main tool
2. `data/evaluation/gold_candidates_discord_conversations.jsonl` - Best output
3. This document - Complete context

### Commands to Remember
```bash
# Generate conversation-based candidates
uv run python utils/gold/harvest_discord_conversations.py \
    --raw-glob "/home/jfrudzinski/work/Discord/Analytics/nomad_discord_Q*_202*/*.json" \
    --out-jsonl data/evaluation/gold_candidates_discord_conversations.jsonl \
    --out-csv data/evaluation/gold_candidates_discord_conversations.csv \
    --write-csv \
    --max-candidates 200

# Quick stats
wc -l data/evaluation/gold_candidates_discord_conversations.jsonl
jq -r '.score' data/evaluation/gold_candidates_discord_conversations.jsonl | sort -rn | head -20

# Mirror the onboarding workshop site and harvest doc-based candidates
wget -m -k -E -np -nH --cut-dirs=0 https://fairmat-nfdi.github.io/nomad-onboarding-workshop/ \
    -P data/fetched/nomad-onboarding-workshop/html
uv run python utils/gold/harvest_gold_from_html.py \
    --html-root data/fetched/nomad-onboarding-workshop/html/nomad-onboarding-workshop \
    --base-url https://fairmat-nfdi.github.io/nomad-onboarding-workshop \
    --min-score 0.55
mv eval/data/gold_candidates.jsonl data/evaluation/gold_candidates_nomad_onboarding_workshop.jsonl
mv eval/data/gold_review.csv data/evaluation/gold_candidates_nomad_onboarding_workshop.csv
python3 - <<'PY'
from pathlib import Path
import json, csv, re
QUESTION_STARTS = (
    'how','what','why','can','is','are','should','does','where','when','who','will','do','could','would','which'
)
def clean_question(text: str) -> str:
    txt = re.sub(r'¶', ' ', text).strip()
    txt = re.sub(r'\s+', ' ', txt)
    txt = re.sub(r'\?+$', '', txt).strip()
    if not txt.endswith('?'):
        txt = f\"{txt}?\"
    return txt
records = []
json_path = Path('data/evaluation/gold_candidates_nomad_onboarding_workshop.jsonl')
for line in json_path.read_text().splitlines():
    if not line.strip():
        continue
    rec = json.loads(line)
    q = rec['question'].strip().lower()
    if rec['question'].strip().endswith('?') or any(q.startswith(p) for p in QUESTION_STARTS):
        rec['question'] = clean_question(rec['question'])
        records.append(rec)
with json_path.open('w', encoding='utf-8') as f:
    for rec in records:
        f.write(json.dumps(rec, ensure_ascii=False) + '\\n')
csv_path = Path('data/evaluation/gold_candidates_nomad_onboarding_workshop.csv')
cols = ["keep","question","proposed_answer","source_url","title","section","method","score","id"]
with csv_path.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=cols)
    writer.writeheader()
    for rec in records:
        writer.writerow({'keep': '', **{k: rec.get(k, '') for k in cols if k != 'keep'}})
print(f\"Final question-like candidates: {len(records)}\")
PY
```

### Decision Points
1. **Review Strategy:** Choose from 4 options above
2. **Approval Threshold:** Recommend score ≥ 0.80 for auto-approval
3. **Target Size:** Current 200 may be too many; consider reducing to 100-150

---

**Last Updated:** December 17, 2025
**Status:** Phase 3 complete, awaiting review strategy decision
**Branch:** extend-gold-eval-set
**Next Agent:** Please review this document and implement chosen review strategy
