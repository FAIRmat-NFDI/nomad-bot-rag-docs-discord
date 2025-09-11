# utils/dynamic_chunking.py
# -*- coding: utf-8 -*-

from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from bs4 import BeautifulSoup

"""
Example usage:

uv run python utils/dynamic_chunking.py \
  --input-root data/fetched \
  --out-path data/chunks/docs.dynamic.jsonl \
  --modes md,html \
  --api-docs-repo-name nomad-api \
  --api-url https://nomad-lab.eu/prod/v1/api/v1/extensions/docs \
  --owner-default FAIRmat-NFDI \
  --branch-default main \
  --md-subdir docs \
  --html-subdir src
"""


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def html_to_markdownish(html: str) -> str:
    """Extract a markdown-ish text from HTML using headings and paragraphs."""
    soup = BeautifulSoup(html or "", "html.parser")
    lines: List[str] = []
    for el in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "code"]
    ):
        name = el.name.lower()
        txt = el.get_text(separator=" ", strip=True)
        if not txt:
            continue
        if name.startswith("h"):
            level = int(name[1])
            lines.append("#" * level + " " + txt)
        elif name == "li":
            lines.append(f"- {txt}")
        elif name in ("pre", "code"):
            lines.append("```")
            lines.append(txt)
            lines.append("```")
        else:
            lines.append(txt)
    return "\n".join(lines)


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
                current_chunk = (
                    (current_chunk + "\n\n" + subsection_heading)
                    if current_chunk
                    else subsection_heading
                )
            continue

        if (
            len(current_chunk) + len(paragraph) > max_chunk_size
            and len(current_chunk) >= min_chunk_size
        ):
            chunks.append(current_chunk.strip())
            if subsection_heading:
                if section_heading and section_heading != subsection_heading:
                    current_chunk = (
                        section_heading + "\n\n" + subsection_heading + "\n\n"
                    )
                else:
                    current_chunk = (subsection_heading or "") + "\n\n"
            elif section_heading:
                current_chunk = section_heading + "\n\n"
            else:
                current_chunk = ""

        current_chunk = (
            (current_chunk + "\n\n" + paragraph) if current_chunk else paragraph
        )

    if current_chunk and len(current_chunk) >= min_chunk_size:
        chunks.append(current_chunk.strip())

    return chunks


# ----------------------------
# Manifests & URL building
# ----------------------------
def load_manifest(manifest_path: Path) -> Dict[str, str]:
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def list_files(
    root: Path, modes: List[str], md_subdir: str, html_subdir: str
) -> List[Path]:
    """
    Look for files only under <root>/<repo>/<mode>/** with mode in {'md','html'}.
    For Markdown, include *all* files under <repo>/md/** (not only md/<md_subdir>/).
    For HTML,     restrict to <repo>/html/<html_subdir>/** (default 'src').
    """
    mode_exts = {"md": {".md", ".mdx"}, "html": {".html"}}
    out: List[Path] = []
    for repo_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for mode in modes:
            mode_dir = repo_dir / mode
            if not mode_dir.is_dir():
                continue
            if mode == "md":
                search_root = mode_dir
            elif mode == "html":
                base_dir = mode_dir / html_subdir
                if not base_dir.is_dir():
                    continue
                search_root = base_dir
            else:
                search_root = mode_dir
            for f in search_root.rglob("*"):
                if f.is_file() and f.suffix.lower() in mode_exts.get(mode, set()):
                    out.append(f)
    return sorted(out)


def _strip_html_prefixes(path: str, html_subdir: str) -> str:
    """Strip 'html/<html_subdir>/' if present, else 'html/'."""
    prefix = f"html/{html_subdir.strip('/')}/"
    if path.startswith(prefix):
        return path[len(prefix) :]
    if path.startswith("html/"):
        return path[len("html/") :]
    return path


def build_source_url_for_md(
    repo: str,
    repo_rel_md: str,
    manifest: Optional[Dict[str, str]],
    owner_default: str,
    branch_default: str,
    md_url_template: str,
    md_blob_url_template: str,
    md_subdir: str,  # kept for signature compatibility; only 'docs' is special-cased
) -> str:
    """
    Special case: only files under md/docs/** are treated as built site pages
    (extension dropped, published URL). All other md/** paths → GitHub blob URL.
    """
    owner = (manifest or {}).get("owner") or owner_default
    repo_name = (manifest or {}).get("repo") or repo
    branch = (manifest or {}).get("branch") or branch_default

    # Only md/docs/** maps to the published site
    if repo_rel_md.startswith("md/docs/"):
        norm = repo_rel_md[len("md/docs/") :]
        if norm.lower().endswith(".md") or norm.lower().endswith(".mdx"):
            norm = norm.rsplit(".", 1)[0]
        tmpl = md_url_template or "https://{owner}.github.io/{repo}/{path}"
        return tmpl.format(owner=owner, repo=repo_name, branch=branch, path=norm)

    # Fallback: any other markdown under md/** → GitHub blob URL (keep extension)
    path_in_repo = repo_rel_md[3:] if repo_rel_md.startswith("md/") else repo_rel_md
    tmpl_blob = (
        md_blob_url_template or "https://github.com/{owner}/{repo}/blob/{branch}/{path}"
    )
    return tmpl_blob.format(
        owner=owner, repo=repo_name, branch=branch, path=path_in_repo
    )


def build_source_url_for_html(
    repo: str,
    repo_rel_html: str,
    manifest: Optional[Dict[str, str]],
    owner_default: str,
    html_url_template: str,
    html_subdir: str,
) -> str:
    # Strip 'html/<html_subdir>/' → site-relative path, then drop 'index.html'
    web_rel = _strip_html_prefixes(repo_rel_html, html_subdir)
    if web_rel.endswith("index.html"):
        web_rel = web_rel[: -len("index.html")]

    # Prefer explicit site base URL from manifest (e.g., https://nomad-lab.eu/nomad-lab/)
    site_base = (manifest or {}).get("site_base_url", "").strip()
    if site_base:
        return (site_base.rstrip("/") + "/" + web_rel.lstrip("/")).rstrip("/")

    # Fallback to owner.github.io pattern
    owner = (manifest or {}).get("owner") or owner_default
    repo_name = (manifest or {}).get("repo") or repo
    tmpl = html_url_template or "https://{owner}.github.io/{repo}/{path}"
    return tmpl.format(owner=owner, repo=repo_name, path=web_rel)


def build_source_url_for_api(api_url: str) -> str:
    return api_url or "https://nomad-lab.eu/prod/v1/api/v1/extensions/docs"


# ----------------------------
# Output rows
# ----------------------------
def write_jsonl(recs, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def build_records_for_file(
    title: str,
    section_title: str,
    chunks: List[str],
    source_url: str,
    repo: str,
    path_original: str,
    path_normalized: str,
    ts_iso: str,
) -> List[Dict]:
    rec_id_prefix = (
        f"docs:{slugify(repo)}:{slugify(title)}:{slugify(section_title)}:dynamic"
    )
    rows = []
    for i, ch in enumerate(chunks):
        rows.append(
            {
                "id": f"{rec_id_prefix}:{i}",
                "source": source_url,
                "repo": repo,
                "title": title,
                "section": section_title,
                "text": ch,
                "path_original": path_original,
                "path_normalized": path_normalized,
                "timestamp": ts_iso,
            }
        )
    return rows


# ----------------------------
# Pipeline
# ----------------------------
def run_dynamic_chunking(
    input_root: str = "external",
    out_path: str = "data/chunks/docs.dynamic.jsonl",
    modes: List[str] = ["md", "html"],
    source_url_template: str = "https://{owner}.github.io/{repo}/{path}",
    html_url_template: str = "https://{owner}.github.io/{repo}/{path}",
    md_blob_url_template: str = "https://github.com/{owner}/{repo}/blob/{branch}/{path}",
    api_docs_repo_name: str = "nomad-api",
    api_url: str = "https://nomad-lab.eu/prod/v1/api/v1/extensions/docs",
    owner_default: str = "FAIRmat-NFDI",
    branch_default: str = "main",
    md_subdir: str = "docs",  # kept for compatibility; only 'docs' is special-cased
    html_subdir: str = "src",
) -> Dict[str, object]:
    root = Path(input_root).resolve()
    out_file = Path(out_path).resolve()

    rows: List[Dict] = []
    files = list_files(root, modes, md_subdir=md_subdir, html_subdir=html_subdir)

    for f in files:
        # <root>/<repo>/<mode>/... → parse from path relative to root
        rel_from_root = f.relative_to(root)
        parts = rel_from_root.parts
        if len(parts) < 3 or parts[1] not in {"md", "html"}:
            continue

        repo = parts[0]  # <repo>
        mode = parts[1]  # md or html
        repo_dir = root / repo
        repo_rel = "/".join(parts[1:])  # includes "md/... or html/..."

        ts = file_mtime_utc_iso(f)
        manifest_path = repo_dir / mode / "manifest.json"
        manifest = load_manifest(manifest_path) if manifest_path.exists() else None

        # Read + normalize to markdown-ish text
        raw = read_text(f)
        textish = html_to_markdownish(raw) if mode == "html" else raw

        # Split into sections
        title = doc_title_from_md(textish, f)
        sections = split_markdown_by_headings(textish) or [("Introduction", textish)]

        # Build source URL + normalized path for metadata
        if repo == api_docs_repo_name and mode == "md":
            page_url = build_source_url_for_api(api_url)
            # normalized path for API docs: mimic docs pages (drop extension)
            if repo_rel.startswith("md/docs/"):
                path_normalized = repo_rel[len("md/docs/") :]
                if path_normalized.lower().endswith(
                    ".md"
                ) or path_normalized.lower().endswith(".mdx"):
                    path_normalized = path_normalized.rsplit(".", 1)[0]
            else:
                # If API repo places md elsewhere, just use file path
                path_normalized = (
                    repo_rel[3:] if repo_rel.startswith("md/") else repo_rel
                )
        elif mode == "html":
            page_url = build_source_url_for_html(
                repo, repo_rel, manifest, owner_default, html_url_template, html_subdir
            )
            path_normalized = _strip_html_prefixes(repo_rel, html_subdir)
            if path_normalized.endswith("index.html"):
                path_normalized = path_normalized[: -len("index.html")]
        else:
            page_url = build_source_url_for_md(
                repo,
                repo_rel,
                manifest,
                owner_default,
                branch_default,
                source_url_template,
                md_blob_url_template,
                md_subdir,
            )
            # Normalized path: drop extension only for md/docs/**; otherwise keep original
            if repo_rel.startswith("md/docs/"):
                path_normalized = repo_rel[len("md/docs/") :]
                if path_normalized.lower().endswith(
                    ".md"
                ) or path_normalized.lower().endswith(".mdx"):
                    path_normalized = path_normalized.rsplit(".", 1)[0]
            else:
                path_normalized = (
                    repo_rel[3:] if repo_rel.startswith("md/") else repo_rel
                )

        for sec_title, sec_text in sections:
            chunks = chunk_content(sec_text)
            if not chunks:
                continue
            rows.extend(
                build_records_for_file(
                    title=title,
                    section_title=sec_title,
                    chunks=chunks,
                    source_url=page_url,
                    repo=repo,
                    path_original=repo_rel,
                    path_normalized=path_normalized,
                    ts_iso=ts,
                )
            )

    write_jsonl(rows, out_file)
    return {
        "files_scanned": len(files),
        "input_root": str(root),
        "out_path": str(out_file),
        "records": len(rows),
    }


# ----------------------------
# CLI
# ----------------------------
def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Chunk docs from <input_root>/<repo>/(md|html) and write JSONL with correct source URLs."
    )
    ap.add_argument(
        "--input-root",
        default="external",
        help="Root containing fetched repos (default: external)",
    )
    ap.add_argument(
        "--out-path",
        default="data/chunks/docs.dynamic.jsonl",
        help="Output JSONL path.",
    )
    ap.add_argument(
        "--modes", default="md,html", help="Comma-separated modes to include: md,html"
    )
    ap.add_argument(
        "--md-subdir",
        default="docs",
        help="Note: only md/docs/** is treated as site pages; all other md/** use GitHub blob URLs.",
    )
    ap.add_argument(
        "--html-subdir",
        default="src",
        help="HTML subdir to include under html/ (default: src)",
    )
    ap.add_argument(
        "--source-url-template",
        default="https://{owner}.github.io/{repo}/{path}",
        help="Template for MD site page URLs (used only for md/docs/**).",
    )
    ap.add_argument(
        "--md-blob-url-template",
        default="https://github.com/{owner}/{repo}/blob/{branch}/{path}",
        help="Template for non-site markdown blob URLs (all md/** except md/docs/**).",
    )
    ap.add_argument(
        "--html-url-template",
        default="https://{owner}.github.io/{repo}/{path}",
        help="Template for HTML (built site) URLs.",
    )
    ap.add_argument(
        "--api-docs-repo-name",
        default="nomad-api",
        help="Repo directory name used for API markdown (default: nomad-api).",
    )
    ap.add_argument(
        "--api-url",
        default="https://nomad-lab.eu/prod/v1/api/v1/extensions/docs",
        help="Landing URL for the API docs UI (used for API markdown).",
    )
    ap.add_argument(
        "--owner-default",
        default="FAIRmat-NFDI",
        help="Default owner if no manifest present.",
    )
    ap.add_argument(
        "--branch-default",
        default="main",
        help="Default branch if no manifest present.",
    )
    return ap.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    stats = run_dynamic_chunking(
        input_root=args.input_root,
        out_path=args.out_path,
        modes=modes,
        source_url_template=args.source_url_template,
        html_url_template=args.html_url_template,
        md_blob_url_template=args.md_blob_url_template,
        api_docs_repo_name=args.api_docs_repo_name,
        api_url=args.api_url,
        owner_default=args.owner_default,
        branch_default=args.branch_default,
        md_subdir=args.md_subdir,
        html_subdir=args.html_subdir,
    )
    print(json.dumps(stats, indent=2))
