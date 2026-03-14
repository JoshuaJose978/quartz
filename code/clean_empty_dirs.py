"""
clean_empty_dirs.py
───────────────────
Remove empty directories from Obsidian vaults.

Skips protected directories: .git, .obsidian, .mypy_cache, __pycache__

Usage:
    python clean_empty_dirs.py                        # uses config.yaml roots
    python clean_empty_dirs.py --dry-run              # preview only
    python clean_empty_dirs.py --roots VaultA VaultB  # explicit vaults
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Directories that must never be removed
PROTECTED = {".git", ".obsidian", ".mypy_cache", "__pycache__", ".venv", "node_modules"}


def is_protected(path: Path) -> bool:
    return any(part in PROTECTED for part in path.parts)


def find_empty_dirs(root: Path) -> list[Path]:
    """Return empty directories under root, deepest first (safe deletion order)."""
    empty = []
    # Walk bottom-up so children are evaluated before parents
    for dirpath in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if not dirpath.is_dir():
            continue
        if is_protected(dirpath):
            continue
        # A dir is "empty" if it contains no files anywhere beneath it
        has_files = any(f.is_file() for f in dirpath.rglob("*"))
        if not has_files:
            empty.append(dirpath)
    return empty


def remove_empty_dirs(roots: list[str], dry_run: bool) -> None:
    total_removed = 0

    for root_str in roots:
        root = Path(root_str)
        if not root.exists():
            print(f"[WARN] Root not found, skipping: {root}")
            continue

        empty = find_empty_dirs(root)
        if not empty:
            print(f"[OK] No empty directories in: {root}")
            continue

        print(f"\n[{root.name}] Found {len(empty)} empty director{'y' if len(empty)==1 else 'ies'}:")
        removed_here = 0
        for d in empty:
            rel = d.relative_to(root.parent)
            if dry_run:
                print(f"  [DRY-RUN] would remove: {rel}")
            else:
                try:
                    d.rmdir()
                    print(f"  [REMOVED] {rel}")
                    removed_here += 1
                except OSError as e:
                    print(f"  [ERROR]   {rel}: {e}")
        total_removed += removed_here

    if dry_run:
        print("\n  Re-run without --dry-run to delete them.")
    else:
        print(f"\n[DONE] Removed {total_removed} empty director{'y' if total_removed==1 else 'ies'}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="clean_empty_dirs",
        description="Remove empty directories from Obsidian vaults.",
    )
    parser.add_argument("--roots", nargs="+", metavar="DIR",
                        help="Vault root directories to clean.")
    parser.add_argument("--config", default="config.yaml",
                        help="config.yaml to read input_roots from (default: config.yaml).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be removed without deleting anything.")
    args = parser.parse_args()

    roots = args.roots
    if not roots:
        try:
            import yaml
            cfg = yaml.safe_load(Path(args.config).read_text())
            roots = cfg.get("input_roots", [])
        except Exception:
            print("[ERROR] Could not load config.yaml. Pass --roots explicitly.")
            sys.exit(1)

    if not roots:
        print("[ERROR] No roots specified.")
        sys.exit(1)

    remove_empty_dirs(roots, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
