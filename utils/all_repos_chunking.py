# utils/docs_dynamic_chunking.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple, Dict


# ----------------------------
# Helpers
# ----------------------------

def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "untitled"

def file_mtime_utc_iso(path: Path) -> str:
    dt = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")

def list_md(root: Path) -> List[Path]:
    exts = {".md", ".mdx"}
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts)

def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def split_markdown_by_headings(md: str) -> List[Tuple[str, str]]:
    lines = (md or "").splitlines()
    sections: List[Tuple[str, str]] = []
    current_title, buf = "Introduction", []
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if buf:
                txt = "\n".join(buf).strip()
                if txt:
                    sections.append((current_title, txt))
                buf = []
            current_title = m.group(2).strip()
        else:
            buf.append(line)
    if buf:
        txt = "\n".join(buf).strip()
        if txt:
            sections.append((current_title, txt))
    return sections

def doc_title_from_md(md: str, path: Path) -> str:
    m = re.search(r"^#\s+(.*)$", md, flags=re.MULTILINE)
    return m.group(1).strip() if m else path.stem.replace("-", " ").title()


# ----------------------------
# Dynamic (heading-aware) chunker
# ----------------------------

def chunk_content(content: str) -> List[str]:
    paragraphs = [p for p in (content or "").split("\n\n") if p.strip()]

    chunks: List[str] = []
    current_chunk = ""
    section_heading = None
    subsection_heading = None
    min_chunk_size = 100
    max_chunk_size = 1000

    for paragraph in paragraphs:
        p = paragraph.strip()
        is_main_heading = p.startswith("# ")
        is_section_heading = p.startswith("## ")
        is_subsection_heading = p.startswith("### ")

        if is_main_heading or is_section_heading:
            if current_chunk and len(current_chunk) >= min_chunk_size:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
            section_heading = paragraph
            subsection_heading = None
            continue

        if is_subsection_heading:
            subsection_heading = paragraph
            if len(current_chunk) >= max_chunk_size * 0.7:
                if current_chunk and len(current_chunk) >= min_chunk_size:
                    chunks.append(current_chunk.strip())
                if section_heading and section_heading != subsection_heading:
                    current_chunk = section_heading + "\n\n" + subsection_heading
                else:
                    current_chunk = subsection_heading
            else:
                current_chunk = (current_chunk + "\n\n" + subsection_heading) if current_chunk else subsection_heading
            continue

        if len(current_chunk) + len(paragraph) > max_chunk_size and len(current_chunk) >= min_chunk_size:
            chunks.append(current_chunk.strip())
            if subsection_heading:
                if section_heading and section_heading != subsection_heading:
                    current_chunk = section_heading + "\n\n" + subsection_heading + "\n\n"
                else:
                    current_chunk = (subsection_heading or "") + "\n\n"
            elif section_heading:
                current_chunk = section_heading + "\n\n"
            else:
                current_chunk = ""

        current_chunk = (current_chunk + "\n\n" + paragraph) if current_chunk else paragraph

    if current_chunk and len(current_chunk) >= min_chunk_size:
        chunks.append(current_chunk.strip())

    return chunks


# ----------------------------
# Path normalization (strip only md/)
# ----------------------------

def normalize_relpath(repo: str, repo_rel: str) -> str:
    """Strip leading 'md/' if present, leave everything else intact."""
    if repo_rel.startswith("md/"):
        return repo_rel[len("md/"):]
    return repo_rel


# ----------------------------
# Output
# ----------------------------

def write_jsonl(recs, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def build_records_for_file(
    md_path: Path,
    root: Path,
    chunks: List[str],
    title: str,
    section_title: str,
    timestamp_iso: str,
    source_url_template: str,
) -> List[Dict]:
    """
    source_url_template supports placeholders:
      {repo}     -> top-level dir under input_root
      {path}     -> normalized path (with md/ stripped)
      {raw_path} -> original repo-relative path
    """
    parts = md_path.relative_to(root).parts
    repo = parts[0] if parts else ""  # top-level dir under data/fetched/
    repo_rel = "/".join(parts[1:]) if len(parts) > 1 else ""
    norm_rel = normalize_relpath(repo, repo_rel)

    rec_id_prefix = f"docs:{slugify(repo)}:{slugify(title)}:{slugify(section_title)}:dynamic"

    page_url = source_url_template.format(repo=repo, path=norm_rel, raw_path=repo_rel).rstrip("/")

    rows = []
    for i, ch in enumerate(chunks):
        rows.append({
            "id": f"{rec_id_prefix}:{i}",
            "source": page_url,          # full link to page (with md/ stripped if present)
            "repo": repo,
            "title": title,
            "section": section_title,
            "text": ch,
            "path_original": repo_rel,
            "path_normalized": norm_rel,
            "timestamp": timestamp_iso,
        })
    return rows


# ----------------------------
# Pipeline
# ----------------------------

def run_dynamic_chunking(
    input_root: str = "data/fetched",
    out_path: str = "data/chunks/docs.dynamic.jsonl",
    source_url_template: str = "https://github.com/FAIRmat-NFDI/{repo}/blob/main/{path}",
) -> Dict[str, object]:
    root = Path(input_root).resolve()
    out_file = Path(out_path).resolve()

    rows: List[Dict] = []
    md_files = list_md(root)
    for p in md_files:
        md = read_markdown(p)
        if not md.strip():
            continue

        title = doc_title_from_md(md, p)
        ts = file_mtime_utc_iso(p)
        sections = split_markdown_by_headings(md)

        for sec_title, sec_text in sections:
            dy = chunk_content(sec_text)
            if not dy:
                continue
            rows.extend(
                build_records_for_file(
                    p, root, dy, title, sec_title, ts, source_url_template
                )
            )

    write_jsonl(rows, out_file)

    return {
        "files_scanned": len(md_files),
        "input_root": str(root),
        "out_path": str(out_file),
        "records": len(rows),
    }


# ----------------------------
# CLI
# ----------------------------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Crawl markdown under data/fetched and emit a dynamic-chunked JSONL with 'source' as a page URL."
    )
    ap.add_argument("--input-root", default="data/fetched", help="Root containing fetched repos.")
    ap.add_argument("--out-path", default="data/chunks/docs.dynamic.jsonl", help="Output JSONL path.")
    ap.add_argument(
        "--source-url-template",
        default="https://github.com/FAIRmat-NFDI/{repo}/blob/main/{path}",
        help="Template for building source URLs. Placeholders: {repo}, {path}, {raw_path}.",
    )
    return ap.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    stats = run_dynamic_chunking(
        input_root=args.input_root,
        out_path=args.out_path,
        source_url_template=args.source_url_template,
    )
    print(json.dumps(stats, indent=2))
