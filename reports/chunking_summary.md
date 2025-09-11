# Chunking Summary

chunked outputs for NOMAD docs (Markdown) and Discord issues forum.

## Files

| source | file | num_chunks | avg_words_per_chunk | path |
|---|---|---:|---:|---|
| docs | nomad_docs.fixed.jsonl | 762 | 139.3 | data/docs/nomad_docs.fixed.jsonl |
| docs | nomad_docs.semantic.jsonl | 2230 | 46.4 | data/docs/nomad_docs.semantic.jsonl |
| docs | nomad_docs.sentence.jsonl | 783 | 132.2 | data/docs/nomad_docs.sentence.jsonl |
| discord | nomad_discord.fixed.jsonl | 545 | 287.1 | data/discord/nomad_discord.fixed.jsonl |
| discord | nomad_discord.semantic.jsonl | 3418 | 42.2 | data/discord/nomad_discord.semantic.jsonl |
| discord | nomad_discord.sentence.jsonl | 599 | 241.0 | data/discord/nomad_discord.sentence.jsonl |

## Notes
- Schema for each record: `{id, source, title, section, text, url, timestamp}`.
- Chunking strategies: `fixed`, `sentence`, `semantic`.
