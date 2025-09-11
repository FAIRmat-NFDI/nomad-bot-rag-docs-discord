#!/usr/bin/env python3
"""
Fetch HTML or Markdown files from a local repo clone and store them in a
snapshot directory, preserving structure.

Examples
--------
# Copy HTML files from a local clone
uv run python utils/fetch_local_content.py \
  --src-dir ../nomad-lab-homepage \
  --mode html \
  --base-dir external \
  --manifest

Notes
-----
- Mode determines default extensions (.html or .md/.mdx).
- By default, the previous snapshot for that mode is replaced.
- Use --no-clean to keep timestamped snapshots.
"""

import argparse, os, re, time, shutil, json
from pathlib import Path
from typing import List


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
        description="Copy HTML/Markdown files from a local repo clone."
    )
    ap.add_argument(
        "--src-dir",
        required=True,
        help="Path to local clone, e.g. ../nomad-lab-homepage",
    )
    ap.add_argument("--mode", choices=["html", "md"], default="html")
    ap.add_argument(
        "--base-dir", default="external", help="Base directory for snapshots"
    )
    ap.add_argument(
        "--include-prefix",
        default="",
        help="Comma-separated subpath prefixes to include",
    )
    ap.add_argument(
        "--exclude-prefix",
        default="",
        help="Comma-separated subpath prefixes to exclude",
    )
    ap.add_argument("--exts", default="", help="Override extensions, e.g. '.md,.rst'")
    ap.add_argument(
        "--manifest", action="store_true", help="Write manifest.json with stats"
    )
    ap.add_argument(
        "--no-clean",
        action="store_true",
        help="Do NOT replace previous snapshot (timestamped dir)",
    )
    args = ap.parse_args()

    src_dir = Path(args.src_dir).resolve()
    default_exts = {"html": [".html"], "md": [".md", ".mdx"]}
    exts = [
        e.strip()
        for e in (args.exts.split(",") if args.exts else default_exts[args.mode])
    ]
    include_list = [s for s in args.include_prefix.split(",") if s.strip()]
    exclude_list = [s for s in args.exclude_prefix.split(",") if s.strip()]

    repo_name = src_dir.name
    base = Path(args.base_dir)
    repo_safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", repo_name)
    dst_root = base / repo_safe / args.mode

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    staging_parent = base / repo_safe / f".staging-{args.mode}-{timestamp}"
    staging_root = staging_parent / args.mode
    staging_root.mkdir(parents=True, exist_ok=True)

    print(f"📂 Scanning {src_dir} for {exts} files…")
    all_files = [p for p in src_dir.rglob("*") if p.is_file()]
    keep = []
    for p in all_files:
        rel = str(p.relative_to(src_dir))
        if should_keep(rel, exts, include_list, exclude_list):
            keep.append((p, rel))

    print(f"🧾 Found {len(all_files)} files; keeping {len(keep)} matching {exts}.")
    downloaded = 0
    for i, (src, rel) in enumerate(keep, 1):
        dest = staging_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        downloaded += 1
        if i % 25 == 0 or i == len(keep):
            print(f"⬇️  [{i}/{len(keep)}] {rel}")

    if args.manifest:
        m = {
            "src_dir": str(src_dir),
            "mode": args.mode,
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
        target = base / repo_safe / f"{args.mode}-{timestamp}"
        staging_parent.rename(target)
        current_link = base / repo_safe / f"{args.mode}-current"
        if current_link.exists() or current_link.is_symlink():
            current_link.unlink()
        current_link.symlink_to(target.resolve())
        print(f"📌 Snapshot saved at: {target} (symlink: {current_link})")
    else:
        atomic_replace(dst_root, staging_root)
        if staging_parent.exists():
            shutil.rmtree(staging_parent, ignore_errors=True)
        print(f"✅ Replaced snapshot at: {dst_root.resolve()}")

    print("🎉 Done.")


if __name__ == "__main__":
    main()
