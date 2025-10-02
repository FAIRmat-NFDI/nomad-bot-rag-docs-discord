#!/usr/bin/env python3
"""
Fetch raw HTML or Markdown files from a GitLab repo branch and store locally,
preserving the directory structure.

Examples
--------
# HTML files from main branch
uv run python scripts/fetch_gitlab_content.py \
  --host https://gitlab.mpcdf.mpg.de \
  --owner nomad-lab \
  --repo nomad-lab-homepage \
  --branch main \
  --mode html \
  --manifest

Notes
-----
- Set GITLAB_TOKEN for private repos (optional).
- Default output root (--base-dir) is external/, with subdir <repo>/<mode>.
- Previous snapshot is replaced unless --no-clean is given.
"""

import argparse, os, time, re, shutil, json
from pathlib import Path
from typing import List, Optional
import requests


def gl_request(
    host: str, path: str, token: Optional[str] = None, params: dict | None = None
):
    url = f"{host.rstrip('/')}/api/v4{path}"
    headers = {"Accept": "application/json"}
    if token:
        headers["PRIVATE-TOKEN"] = token
    r = requests.get(url, headers=headers, params=params, timeout=60)
    r.raise_for_status()
    return r


def gl_project_path(owner: str, repo: str) -> str:
    return requests.utils.quote(f"{owner}/{repo}", safe="")


def get_branch_commit_sha(
    host: str, owner: str, repo: str, branch: str, token: Optional[str]
) -> str:
    project = gl_project_path(owner, repo)
    data = gl_request(
        host, f"/projects/{project}/repository/branches/{branch}", token
    ).json()
    return data["commit"]["id"]


def get_tree_recursive(
    host: str, owner: str, repo: str, ref: str, token: Optional[str]
) -> list[dict]:
    project = gl_project_path(owner, repo)
    page, per_page = 1, 100
    all_items = []
    while True:
        resp = gl_request(
            host,
            f"/projects/{project}/repository/tree",
            token,
            params={"ref": ref, "recursive": True, "per_page": per_page, "page": page},
        )
        items = resp.json()
        if not items:
            break
        all_items.extend(items)
        if len(items) < per_page:
            break
        page += 1
    return [{"type": x.get("type"), "path": x.get("path")} for x in all_items]


def raw_url(host: str, owner: str, repo: str, branch: str, path: str) -> str:
    return f"{host.rstrip('/')}/{owner}/{repo}/-/raw/{branch}/{path}?inline=false"


def should_keep(
    path: str, exts: List[str], include_prefix: List[str], exclude_prefix: List[str]
) -> bool:
    if not any(path.endswith(ext) for ext in exts):
        return False
    for ex in exclude_prefix:
        if ex and path.startswith(ex):
            return False
    if include_prefix:
        return any(path.startswith(inc) for inc in include_prefix if inc)
    return True


def download_file(url: str, dest_path: Path, token: Optional[str] = None):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {}
    if token:
        headers["PRIVATE-TOKEN"] = token
    with requests.get(url, headers=headers, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 14):
                if chunk:
                    f.write(chunk)


def atomic_replace(dst: Path, staging: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    staging.rename(dst)


def main():
    ap = argparse.ArgumentParser(
        description="Download HTML/Markdown files from a GitLab repo branch."
    )
    ap.add_argument(
        "--host",
        required=True,
        help="GitLab host base URL, e.g. https://gitlab.mpcdf.mpg.de",
    )
    ap.add_argument("--owner", required=True, help="Namespace/group, e.g. nomad-lab")
    ap.add_argument(
        "--repo", required=True, help="Project name, e.g. nomad-lab-homepage"
    )
    ap.add_argument("--branch", default="main")
    ap.add_argument("--mode", choices=["html", "md"], default="html")
    ap.add_argument("--base-dir", default="external")
    ap.add_argument("--include-prefix", default="")
    ap.add_argument("--exclude-prefix", default="")
    ap.add_argument("--exts", default="")
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--no-clean", action="store_true")
    args = ap.parse_args()

    token = os.getenv("GITLAB_TOKEN")
    owner, repo, branch, mode = args.owner, args.repo, args.branch, args.mode
    default_exts = {"html": [".html"], "md": [".md", ".mdx"]}
    exts = [
        e.strip() for e in (args.exts.split(",") if args.exts else default_exts[mode])
    ]
    include_list = [s for s in args.include_prefix.split(",") if s.strip()]
    exclude_list = [s for s in args.exclude_prefix.split(",") if s.strip()]

    base = Path(args.base_dir)
    repo_safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", args.repo)
    dst_root = base / repo_safe / mode
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    staging_parent = base / repo_safe / f".staging-{mode}-{timestamp}"
    staging_root = staging_parent / mode
    staging_root.mkdir(parents=True, exist_ok=True)

    print(f"🔎 Resolving branch '{branch}' for {owner}/{repo} …")
    sha = get_branch_commit_sha(args.host, owner, repo, branch, token)
    print(f"✅ Branch {branch} @ {sha}")

    print("📂 Listing tree (recursive)…")
    tree = get_tree_recursive(args.host, owner, repo, branch, token)
    blobs = [t for t in tree if t.get("type") == "blob"]
    keep = [
        f for f in blobs if should_keep(f["path"], exts, include_list, exclude_list)
    ]
    print(f"🧾 Found {len(blobs)} files; keeping {len(keep)} matching {exts}.")

    downloaded = 0
    for i, f in enumerate(keep, 1):
        rel_path = f["path"]
        url = raw_url(args.host, owner, repo, branch, rel_path)
        try:
            download_file(url, staging_root / rel_path, token=token)
            downloaded += 1
            if i % 25 == 0 or i == len(keep):
                print(f"⬇️  [{i}/{len(keep)}] {rel_path}")
        except Exception as e:
            print(f"❌ Failed: {rel_path} — {e}")

    if args.manifest:
        m = {
            "host": args.host,
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
        (staging_root / "manifest.json").write_text(
            json.dumps(m, indent=2), encoding="utf-8"
        )

    if args.no_clean:
        target = base / repo_safe / f"{mode}-{timestamp}"
        staging_parent.rename(target)
        current_link = base / repo_safe / f"{mode}-current"
        if current_link.exists() or current_link.is_symlink():
            current_link.unlink()
        current_link.symlink_to(target.resolve())
        print(f"📌 Snapshot saved at: {target} (symlink: {current_link})")
    else:
        atomic_replace(dst_root, staging_root)
        if staging_parent.exists():
            shutil.rmtree(staging_parent, ignore_errors=True)
        print(f"✅ Replaced snapshot at: {dst_root.resolve()}")

    print(f"🎉 Done.")


if __name__ == "__main__":
    main()
