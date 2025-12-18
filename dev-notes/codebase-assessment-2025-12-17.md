# Codebase Assessment – 17 Dec 2025

This document captures the current state of the NOMAD RAG Assistant repository and outlines concrete recommendations for the next engineering cycles. It reflects the repo as of 17 Dec 2025 (`extend-gold-eval-set` branch) and synthesizes learnings from the recent documentation/Discord harvesting work.

---

## 1. Architecture Snapshot

| Pillar | Summary |
| --- | --- |
| **RAG Runtime** | `src/nomad_ragbot` houses the FastAPI backend (`api/`), the `RAGQueryEngine` (`query/`), shared LLM/embedding clients, and the stand-alone Gradio UI. The API is responsible for indexing data into Chroma and serving `/ask`. |
| **Evaluation Suite** | `data/evaluation` + `eval/` power the gold-standard QA benchmarking. `ragbot-eval` and `ragbot-eval-dash` consume `gold_all.jsonl` plus run outputs in `runs/`. |
| **Data Harvesting** | `utils/gold` contains generators and filters for docs, Discord, and glossary Q&A. Recent additions (`harvest_gold_from_markdown.py`, `harvest_discord_conversations.py`, `harvest_discord_issues.py`) feed the human review queue. |
| **Datasets** | `data/chunks` (retrieval corpus), `data/evaluation/gold_all.jsonl` (105 original + recent adds), `data/evaluation/gold_candidates_*.{jsonl,csv,md}` (review queues). |

This separation is clean and makes it easy to focus on a subsystem (runtime vs. eval vs. harvesting) without cross-contamination.

---

## 2. Strengths Observed

1. **Modular source layout** (`src/nomad_ragbot/...`) + `pyproject.toml` managed through `uv`. Easy to install, reason about, and deploy.
2. **Rich tooling around data quality** – Markdown/Discord harvesters, deduplication heuristics, reviewer-friendly Markdown exports, etc.
3. **Evaluation-first culture** – automated scripts for LLM-judged evals, dashboards, and explicit gold datasets provide reproducibility.
4. **Documentation** – the README plus `docs/gold_candidate_generation_status.md` capture workflows in detail, lowering onboarding cost.

---

## 3. Gaps & Risks

1. **Testing coverage**  
   - Core RAG logic (`query/`) and API endpoints lack automated tests (unit or integration).  
   - Harvesters are complex but untested, so regressions (e.g., leaking PII, duplicate Qs) are possible.

2. **Data-review throughput bottleneck**  
   - Manual marking of hundreds of candidates remains tedious. Auto-triage exists (scores, heuristics) but is not integrated into review tools.  
   - No script converts reviewer Markdown decisions back into `gold_all.jsonl` yet.

3. **Gold dataset hygiene**  
   - `gold_all.jsonl` appends are ad-hoc; duplicates or conflicting versions can sneak in.  
   - There is no validation hook (schema or linter) before merges.

4. **Runtime observability**  
   - FastAPI service lacks health metrics, structured logging, or guardrails for long-running retrieval/LLM calls.  
   - Hard to evaluate query latency, failure rates, or content safety issues in production.

5. **LLM dependency management**  
   - Embedding/generation endpoints are configured via `.env`, but there is no fallback or automatic retry strategy if an upstream model fails.

6. **Security/privacy for harvested data**  
   - Discord harvesters now strip names, but there is no automated check for PII.  
   - Doc harvesters may still include stale TODO notes, outdated instructions, or internal paths.

---

## 4. Recommendations & Strategy

### A. Short-Term (next sprint)
1. **Fast ingestion loop for accepted candidates**  
   - Script to parse `gold_candidates_*_review.md`, capture `[x] Accept`, inject edits into `gold_all.jsonl`, and re-run dedup/schema validation.
2. **Gold dataset validation**  
   - Add `tools/jsonl_validate.py` check to CI + `pre-commit` so `gold_all.jsonl` must pass schema/dedup/PII rules before merging.
3. **Basic unit tests**  
   - Target `src/nomad_ragbot/query/query.py` (retrieval pipeline) and `utils/gold/harvest_discord_issues.py` (edge-case summarization).  
   - Run via `uv run pytest tests/`.
4. **Observability scaffolding**  
   - Add structured logging (e.g., `loguru` or stdlib) + request timing to FastAPI.  
   - Provide a `/health` endpoint that verifies Chroma + model backends.

### B. Medium-Term
1. **Reviewer UI**  
   - Convert Markdown review workflow into a minimal web tool (Streamlit/Gradio) that shows context, lets reviewers edit Q/A, and records decisions directly in JSON.  
   - Support filters (score thresholds, topic, source) to prioritize review.
2. **Dataset versioning**  
   - Introduce `data/evaluation/gold_all.v{N}.jsonl` or DVC so we can track incremental changes, revert, and compare evaluation results over time.
3. **RAG experimentation harness**  
   - Provide config-driven experiments (prompt templates, rerankers, top-k) and auto-log them to `runs/`.  
   - Combine with the evaluation suite to produce dashboards per experiment.
4. **Runtime guardrails**  
   - Integrate content filters (PII, toxicity) + caching for repeated queries.  
   - Add concurrency limits, timeouts, and better error reports for downstream LLM failures.

### C. Long-Term
1. **Continuous data curation**  
   - Automate documentation harvesting (GitHub Actions) + schedule Discord ingestion so new issues are flagged for review weekly.  
   - Explore semi-supervised quality scoring to auto-accept high-confidence candidates.
2. **Feedback loop & instrumentation**  
   - Log user feedback from the Gradio UI/API; use it to retrain rerankers, adjust prompts, or promote/demote data sources.  
   - Instrument retrieval (top-k hits, source diversity) to detect knowledge gaps.
3. **Plugin ecosystem**  
   - Align harvester scripts with a plugin interface so new sources (e.g., GitHub Issues, Slack) can be dropped in without copy/pasting code.

---

## 5. Suggested Next Steps

1. Land ingestion script for Markdown review decisions + integrate with CI validation.
2. Add foundational tests for the query engine + at least one harvester.
3. Ship FastAPI health/logging improvements so we can deploy confidently.
4. Prioritize reviewer UX improvements (web tool or more ergonomic Markdown templates) to keep the gold dataset growing without burning out reviewers.

These investments keep the RAG system reliable, scalable, and auditable as NOMAD’s documentation and Discord traffic continue to grow.

