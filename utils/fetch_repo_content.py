#!/usr/bin/env python3
"""
Fetch raw HTML or Markdown files from a GitHub repo branch and store locally,
preserving the directory structure, with clean snapshots per mode (html|md).

Examples
--------
# HTML from gh-pages (built site), stored under external/html/
uv run python scripts/fetch_repo_content.py \
  --owner FAIRmat-NFDI --repo nomad-docs --branch gh-pages --mode html

# Markdown from main (source docs), stored under external/md/
uv run python scripts/fetch_repo_content.py \
  --owner FAIRmat-NFDI --repo nomad-docs --branch main --mode md \
  --include-prefix docs/

Notes
-----
- Set GITHUB_TOKEN to increase rate limits (optional).
- Default output root (--base-dir) is external/, with subdir per mode.
- By default, the previous snapshot for that mode is atomically replaced.
"""

import argparse
import os
import time
import shutil
from pathlib import Path
from typing import List, Optional

import requests

GITHUB_API = "https://api.github.com"


def gh_request(
    url: str,
    token: Optional[str] = None,
    params: dict | None = None,
    accept: str | None = None,
):
    headers = {"Accept": accept or "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=headers, params=params, timeout=60)
    if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
        reset = int(r.headers.get("X-RateLimit-Reset", "0"))
        wait = max(reset - int(time.time()), 1)
        print(f"⚠️  Rate limit hit. Sleeping {wait}s until reset…")
        time.sleep(wait)
        r = requests.get(url, headers=headers, params=params, timeout=60)
    r.raise_for_status()
    return r


def get_branch_commit_sha(
    owner: str, repo: str, branch: str, token: Optional[str]
) -> str:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/branches/{branch}"
    data = gh_request(url, token).json()
    return data["commit"]["sha"]


def get_tree_recursive(
    owner: str, repo: str, tree_sha: str, token: Optional[str]
) -> list[dict]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{tree_sha}"
    data = gh_request(url, token, params={"recursive": "1"}).json()
    if data.get("truncated"):
        print(
            "⚠️  Warning: tree listing is truncated; consider narrowing scope with --include-prefix."
        )
    return data.get("tree", [])


def raw_url(owner: str, repo: str, branch: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"


def should_keep(
    path: str, exts: List[str], include_prefix: List[str], exclude_prefix: List[str]
) -> bool:
    if not any(path.endswith(ext) for ext in exts):
        return False
    for ex in exclude_prefix:
        ex = ex.strip()
        if ex and path.startswith(ex):
            return False
    if include_prefix:
        return any(
            path.startswith(inc.strip()) for inc in include_prefix if inc.strip()
        )
    return True


def download_file(
    url: str,
    dest_path: Path,
    token: Optional[str] = None,
    try_index_fallback: bool = True,
):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with requests.get(url, headers=headers, stream=True, timeout=120) as r:
        if (
            r.status_code == 404
            and try_index_fallback
            and not url.endswith("/index.html")
        ):
            alt = url.rstrip("/") + "/index.html"
            with requests.get(alt, headers=headers, stream=True, timeout=120) as r2:
                r2.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in r2.iter_content(chunk_size=1 << 14):
                        if chunk:
                            f.write(chunk)
            return
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 14):
                if chunk:
                    f.write(chunk)


def atomic_replace(dst: Path, staging: Path):
    # Remove existing destination and move staging into place atomically
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    staging.rename(dst)


def main():
    ap = argparse.ArgumentParser(
        description="Download HTML or Markdown files from a GitHub repo branch."
    )
    ap.add_argument(
        "--owner", required=True, help="GitHub org/user, e.g., FAIRmat-NFDI"
    )
    ap.add_argument("--repo", required=True, help="Repository name, e.g., nomad-docs")
    ap.add_argument(
        "--branch", default="gh-pages", help="Branch to fetch from (default: gh-pages)"
    )
    ap.add_argument(
        "--mode",
        choices=["html", "md"],
        default="html",
        help="What to fetch (default: html)",
    )
    ap.add_argument(
        "--base-dir",
        default="external",
        help="Base directory for snapshots (default: external)",
    )
    ap.add_argument(
        "--include-prefix", default="", help="Comma-separated path prefixes to include"
    )
    ap.add_argument(
        "--exclude-prefix", default="", help="Comma-separated path prefixes to exclude"
    )
    ap.add_argument(
        "--exts", default="", help="Override file extensions, e.g. '.md,.mdx,.rst'"
    )
    ap.add_argument(
        "--manifest",
        action="store_true",
        help="Write a manifest.json with commit SHA and file counts",
    )
    ap.add_argument(
        "--no-clean",
        action="store_true",
        help="Do NOT replace previous snapshot (write into timestamped dir)",
    )
    args = ap.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    owner, repo, branch, mode = args.owner, args.repo, args.branch, args.mode

    # Defaults by mode
    default_exts = {"html": [".html"], "md": [".md", ".mdx"]}
    exts = [
        e.strip() for e in (args.exts.split(",") if args.exts else default_exts[mode])
    ]
    include_list = [s for s in args.include_prefix.split(",") if s.strip()]
    exclude_list = [s for s in args.exclude_prefix.split(",") if s.strip()]

    # Compute destination paths
    base = Path(args.base_dir)
    dst_root = base / mode  # e.g., external/html or external/md

    # If not cleaning, write into a timestamped subfolder and leave a 'current' symlink
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    staging_parent = base / f".staging-{mode}-{timestamp}"
    staging_root = staging_parent / mode

    print(f"🔎 Resolving branch '{branch}' for {owner}/{repo} …")
    sha = get_branch_commit_sha(owner, repo, branch, token)
    print(f"✅ Branch {branch} @ {sha}")

    print("📂 Listing tree (recursive)…")
    tree = get_tree_recursive(owner, repo, sha, token)
    blobs = [t for t in tree if t.get("type") == "blob"]

    keep = [
        f for f in blobs if should_keep(f["path"], exts, include_list, exclude_list)
    ]
    print(
        f"🧾 Found {len(blobs)} files; keeping {len(keep)} file(s) matching {exts} with filters."
    )

    downloaded = 0
    for i, f in enumerate(keep, 1):
        rel_path = f["path"]
        url = raw_url(owner, repo, branch, rel_path)
        dest_path = staging_root / rel_path
        try:
            # index.html fallback only makes sense for HTML mode
            download_file(
                url, dest_path, token=token, try_index_fallback=(mode == "html")
            )
            downloaded += 1
            if i % 25 == 0 or i == len(keep):
                print(f"⬇️  [{i}/{len(keep)}] {rel_path}")
        except Exception as e:
            print(f"❌ Failed: {rel_path} — {e}")

    # Write manifest (in staging)
    if args.manifest:
        import json

        m = {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "commit_sha": sha,
            "mode": mode,
            "extensions": exts,
            "include_prefix": include_list,
            "exclude_prefix": exclude_list,
            "downloaded": downloaded,
            "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        (staging_root / "manifest.json").parent.mkdir(parents=True, exist_ok=True)
        (staging_root / "manifest.json").write_text(
            json.dumps(m, indent=2), encoding="utf-8"
        )

    staging_parent.mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)

    if args.no_clean:
        # keep timestamped snapshot and update a 'current' symlink for convenience
        target = base / f"{mode}-{timestamp}"
        staging_parent.rename(target)
        current_link = base / f"{mode}-current"
        if current_link.exists() or current_link.is_symlink():
            current_link.unlink()
        current_link.symlink_to(target.resolve())
        print(f"📌 Snapshot saved at: {target} (symlink: {current_link})")
    else:
        # atomically replace the previous mode directory
        atomic_replace(dst_root, staging_root)
        # remove the empty staging parent
        if staging_parent.exists():
            shutil.rmtree(staging_parent, ignore_errors=True)
        print(f"✅ Replaced snapshot at: {dst_root.resolve()} (clean state)")

    print(
        f"🎉 Done. Files saved under: {(base / (mode if not args.no_clean else f'{mode}-{timestamp}')).resolve()}"
    )


if __name__ == "__main__":
    main()
