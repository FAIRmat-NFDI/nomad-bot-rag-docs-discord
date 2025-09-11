#!/usr/bin/env python3
import os, re, sys, subprocess
from pathlib import Path
from urllib.parse import urlparse

LINKS_FILE = "../data/documentation_links.txt"
FETCHER = "./fetch_repo_content.py"   # your existing script
BASE_DIR = "../data/fetched"                      # where snapshots land

# simple helpers
GITHUB_RE = re.compile(r"^https?://github\.com/([^/]+)/([^/]+)(?:/.*)?$")
RAW_RE    = re.compile(r"^https?://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)$")
PAGES_RE  = re.compile(r"^https?://([^/.]+)\.github\.io/([^/]+)/(.*)?$")

def parse_link(url: str):
    """Return dict: {owner, repo, branch, mode, include_prefix}"""
    url = url.strip()
    if not url or url.startswith("#"):
        return None

    # raw.githubusercontent
    m = RAW_RE.match(url)
    if m:
        owner, repo, branch, path = m.groups()
        mode = "md" if path.lower().endswith((".md", ".mdx")) else "html"
        return dict(owner=owner, repo=repo, branch=branch, mode=mode,
                    include_prefix=path)

    # github pages
    m = PAGES_RE.match(url)
    if m:
        owner_sub, repo, rest = m.groups()
        # GitHub Pages are built from gh-pages by convention
        return dict(owner=owner_sub, repo=repo, branch="gh-pages",
                    mode="html", include_prefix=(rest or "").strip("/"))

    # github.com
    if "github.com/" in url:
        parts = urlparse(url).path.strip("/").split("/")
        # /OWNER/REPO
        if len(parts) == 2:
            owner, repo = parts
            # default to main branch, mode md (docs)
            return dict(owner=owner, repo=repo, branch="main",
                        mode="md", include_prefix="")
        # /OWNER/REPO/tree/BRANCH/path...
        if len(parts) >= 4 and parts[2] == "tree":
            owner, repo, _, branch = parts[:4]
            subpath = "/".join(parts[4:]) if len(parts) > 4 else ""
            mode = "md"  # assume source docs unless you target gh-pages explicitly
            return dict(owner=owner, repo=repo, branch=branch,
                        mode=mode, include_prefix=subpath)
        # /OWNER/REPO/blob/BRANCH/path/to/file
        if len(parts) >= 4 and parts[2] == "blob":
            owner, repo, _, branch = parts[:4]
            file_path = "/".join(parts[4:])
            mode = "md" if file_path.lower().endswith((".md", ".mdx")) else "html"
            return dict(owner=owner, repo=repo, branch=branch,
                        mode=mode, include_prefix=file_path)

    # unknown / non-github → skip
    return None

def main():
    links_path = Path(LINKS_FILE)
    if not links_path.exists():
        print(f"❌ Links file not found: {links_path.resolve()}")
        sys.exit(1)

    tasks = []
    for line in links_path.read_text(encoding="utf-8").splitlines():
        info = parse_link(line.strip())
        if not info:
            continue
        tasks.append(info)

    # de-dup identical tasks
    dedup = {(t["owner"], t["repo"], t["branch"], t["mode"], t["include_prefix"]) for t in tasks}
    print(f"🔎 Parsed {len(tasks)} URLs → {len(dedup)} unique fetch tasks")

    for owner, repo, branch, mode, inc in sorted(dedup):
        cmd = [
            sys.executable, FETCHER,
            "--owner", owner,
            "--repo", repo,
            "--branch", branch,
            "--mode", mode,
            "--base-dir", BASE_DIR,
            "--manifest"
        ]
        if inc:
            cmd += ["--include-prefix", inc]
        print("➡️ ", " ".join(cmd))
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print(f"⚠️  Fetch failed for {owner}/{repo}@{branch} ({mode}) include={inc}")

    print("🎉 All fetches attempted.")
    print(f"📂 Content staged under: {Path(BASE_DIR).resolve()} (per repo: external/<repo>/(md|html))")

if __name__ == "__main__":
    main()
