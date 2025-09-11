#!/usr/bin/env python3
"""
build_api_docs_from_openapi.py

Fetch NOMAD OpenAPI JSON and render per-tag Markdown files ready for your docs
chunking workflow. By default, writes to external/nomad-api/md/.

Usage (Markdown only):
  uv run python utils/build_api_docs_from_openapi.py \
    --openapi-url https://nomad-lab.eu/prod/v1/api/v1/openapi.json

Optional JSONL (endpoint-level units, if you ever want it):
  uv run python utils/build_api_docs_from_openapi.py \
    --openapi-url https://nomad-lab.eu/prod/v1/api/v1/openapi.json \
    --out-jsonl data/nomad_api_chunks.jsonl

Include a manifest (URL, date, SHA256):
  uv run python utils/build_api_docs_from_openapi.py \
    --openapi-url https://nomad-lab.eu/prod/v1/api/v1/openapi.json \
    --manifest
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


# -------------------------
# HTTP + small utils
# -------------------------
def fetch_json(url: str) -> dict:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def md_escape(s: str) -> str:
    return s.replace("<", "&lt;").replace(">", "&gt;")


def short_type(schema: dict) -> str:
    if not isinstance(schema, dict):
        return ""
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    t = schema.get("type")
    fmt = schema.get("format")
    if t and fmt:
        return f"{t} ({fmt})"
    return t or "object"


def schema_name_from_ref(ref: str) -> str:
    return ref.split("/")[-1]


def param_table(params: List[dict]) -> str:
    if not params:
        return ""
    rows = [
        "| Name | In | Type | Required | Description |",
        "|---|---|---|---|---|",
    ]
    for p in params:
        typ = short_type(p.get("schema", {}))
        desc = p.get("description", "") or ""
        rows.append(
            f"| `{p.get('name')}` | {p.get('in')} | {typ} | {p.get('required', False)} | {md_escape(desc)} |"
        )
    return "\n".join(rows) + "\n"


def minimal_example(
    method: str,
    server: str,
    path: str,
    params: List[dict] | None,
    request_body: dict | None,
) -> Tuple[str, str]:
    """Return tiny curl + python examples. Avoid heavy payloads."""
    url = server.rstrip("/") + path
    q_params = [p for p in (params or []) if p.get("in") == "query"]
    curl = f"curl -X {method.upper()} '{url}'"
    py_lines = ["import requests", f"url = '{url}'"]

    if q_params:
        # show one query param only
        k = q_params[0]["name"]
        curl = f"curl -X {method.upper()} '{url}?{k}=<value>'"
        py_lines.append(f"params = {{'{k}': '<value>'}}")
        if method.lower() == "get":
            py_lines.append("r = requests.get(url, params=params, timeout=60)")
        else:
            py_lines.append(
                f"r = requests.request('{method.upper()}', url, params=params, json={{}}, timeout=60)"
            )
    else:
        if method.lower() == "get":
            py_lines.append("r = requests.get(url, timeout=60)")
        else:
            py_lines.append(
                f"r = requests.request('{method.upper()}', url, json={{}}, timeout=60)"
            )
    py_lines.append("print(r.status_code); print(r.text[:500])")

    return curl, "\n".join(py_lines)


# -------------------------
# Build Markdown + optional JSONL
# -------------------------
def build_markdown_and_jsonl(
    openapi: dict,
    out_md_dir: Path,
    out_jsonl: Optional[Path] = None,
) -> None:
    servers = [s.get("url") for s in openapi.get("servers", [])] or [""]
    server = servers[0]  # primary
    tags = {t["name"]: t.get("description", "") for t in openapi.get("tags", [])}
    paths = openapi.get("paths", {}) or {}

    # group endpoints by tag
    by_tag: Dict[str, List[dict]] = {}
    for path, methods in paths.items():
        for method, meta in (methods or {}).items():
            if method.lower() not in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
            }:
                continue
            entry = {
                "method": method.upper(),
                "path": path,
                "operationId": meta.get("operationId", f"{method}_{path}"),
                "summary": meta.get("summary", "") or "",
                "description": meta.get("description", "") or "",
                "parameters": meta.get("parameters", []) or [],
                "requestBody": meta.get("requestBody", {}) or {},
                "response200": (meta.get("responses", {}) or {}).get("200") or {},
                "tags": meta.get("tags", ["untagged"]) or ["untagged"],
            }
            for tg in entry["tags"]:
                by_tag.setdefault(tg, []).append(entry)

    out_md_dir.mkdir(parents=True, exist_ok=True)
    snapshot_date = time.strftime("%Y-%m-%d")
    jsonl_lines: List[dict] = []

    for tag, entries in sorted(by_tag.items(), key=lambda kv: kv[0].lower()):
        md_lines: List[str] = []
        md_lines.append(f"# {tag}\n")
        if tags.get(tag):
            md_lines.append(tags[tag] + "\n")

        for e in sorted(entries, key=lambda d: (d["path"], d["method"])):
            md_lines.append(f"## {e['method']} {e['path']}\n")
            if e["summary"]:
                md_lines.append(f"**Summary:** {md_escape(e['summary'])}\n")
            if e["description"]:
                md_lines.append(md_escape(e["description"]) + "\n")

            if e["parameters"]:
                md_lines.append("### Parameters\n")
                md_lines.append(param_table(e["parameters"]))

            if e["requestBody"]:
                md_lines.append("### Request Body (short)\n")
                rb = e["requestBody"].get("content", {}).get("application/json", {})
                schema = rb.get("schema", {})
                if "$ref" in schema:
                    md_lines.append(
                        f"*Schema:* `{schema_name_from_ref(schema['$ref'])}`\n"
                    )
                else:
                    md_lines.append(f"*Type:* {short_type(schema)}\n")

            if e["response200"]:
                md_lines.append("### Response (200) — short\n")
                c = e["response200"].get("content", {}).get("application/json", {})
                schema = c.get("schema", {})
                if "$ref" in schema:
                    md_lines.append(
                        f"*Schema:* `{schema_name_from_ref(schema['$ref'])}`\n"
                    )
                else:
                    md_lines.append(f"*Type:* {short_type(schema)}\n")

            curl, py = minimal_example(
                e["method"], server, e["path"], e["parameters"], e["requestBody"]
            )
            md_lines.append("### Examples\n")
            md_lines.append("**curl**\n")
            md_lines.append("```bash\n" + curl + "\n```\n")
            md_lines.append("**python (requests)**\n")
            md_lines.append("```python\n" + py + "\n```\n")

            swagger_base = f"{server.rstrip('/')}/extensions/docs"
            md_lines.append(f"*operationId:* `{e['operationId']}`  \n")
            md_lines.append(f"*source_url:* {swagger_base}\n")

            if out_jsonl:
                # Just the current endpoint section (last added block)
                endpoint_blob = "\n".join(md_lines[-25:])
                jsonl_lines.append(
                    {
                        "id": f"{tag}::{e['method']}::{e['path']}",
                        "text": endpoint_blob,
                        "source": "nomad-api",
                        "tag": tag,
                        "method": e["method"],
                        "path": e["path"],
                        "operationId": e["operationId"],
                        "source_url": swagger_base,
                        "snapshot_date": snapshot_date,
                    }
                )

        # write per-tag Markdown
        filename = out_md_dir / f"api_{re.sub(r'[^A-Za-z0-9_-]+', '-', tag.lower())}.md"
        filename.write_text("\n".join(md_lines), encoding="utf-8")

    if out_jsonl and jsonl_lines:
        out_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with open(out_jsonl, "w", encoding="utf-8") as f:
            for row in jsonl_lines:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")


# -------------------------
# Main
# -------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--openapi-url",
        default="https://nomad-lab.eu/prod/v1/api/v1/openapi.json",
        help="OpenAPI JSON URL to fetch",
    )
    ap.add_argument(
        "--out-md-dir",
        default="external/nomad-api/md",
        help="Directory to store per-tag Markdown files",
    )
    ap.add_argument(
        "--out-jsonl",
        default="",
        help="Optional path to write endpoint-level JSONL (one item per endpoint)",
    )
    ap.add_argument(
        "--manifest",
        action="store_true",
        help="Write a manifest.json next to the Markdown outputs",
    )
    args = ap.parse_args()

    out_md_dir = Path(args.out_md_dir)
    out_jsonl = Path(args.out_jsonl) if args.out_jsonl else None

    print(f"Fetching OpenAPI: {args.openapi_url}")
    # Also keep the raw bytes for hashing the spec
    r = requests.get(args.openapi_url, timeout=60)
    r.raise_for_status()
    openapi = r.json()
    spec_hash = sha256_bytes(r.content)

    build_markdown_and_jsonl(openapi, out_md_dir, out_jsonl)

    if args.manifest:
        manifest = {
            "openapi_url": args.openapi_url,
            "snapshot_date": time.strftime("%Y-%m-%d"),
            "sha256": spec_hash,
            "outputs": {
                "md_dir": str(out_md_dir.resolve()),
                "jsonl": str(out_jsonl.resolve()) if out_jsonl else None,
            },
        }
        (out_md_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        print(f"Wrote manifest: {(out_md_dir / 'manifest.json').resolve()}")

    print(f"Done. Markdown in: {out_md_dir.resolve()}")
    if out_jsonl:
        print(f"JSONL in: {out_jsonl.resolve()}")


if __name__ == "__main__":
    main()
