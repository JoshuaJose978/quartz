"""
add_links.py
────────────
Inject Obsidian [[wiki-links]] into every Markdown note so the graph view
becomes richly connected.

Strategy (per vault, fully self-contained):
  1. Category links  — every note links to its same-folder siblings
                       (hub-and-spoke within each category folder).
  2. Cross-category  — keyword overlap between note stems finds notes
                       in *other* categories that share significant terms.
  3. A "## Related Notes" section is appended (or updated) at the bottom
     of each file.  Existing links in the body are never touched.

Obsidian wiki-link format:  [[Note Name]]   (no .md, no path — Obsidian
resolves by filename uniqueness within the vault).

Usage:
    python add_links.py                    # uses config.yaml roots, dry-run off
    python add_links.py --dry-run          # preview only, no files written
    python add_links.py --roots VaultA     # single vault
    python add_links.py --max-same 6 --max-cross 3
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── stop-words for keyword extraction ────────────────────────────────────────
STOP = {
    "a","an","and","are","as","at","be","by","do","for","from","has","he",
    "in","is","it","its","of","on","or","that","the","this","to","was","will",
    "with","you","your","we","i","my","our","their","they","all","also","but",
    "can","get","had","have","how","if","into","just","make","more","no","not",
    "one","only","other","out","over","so","some","than","then","there","these",
    "up","use","using","what","when","which","who","would","about","after",
    "before","between","been","could","do","does","during","each","few","final",
    "first","for","guide","how","introduction","notes","note","overview",
    "practical","summary","understanding","versus","via","vs","with","within",
    "new","old","part","page","questions","question","solutions","solution",
    "the","to","complete","comprehensive","advanced","basic","quick","simple",
}

RELATED_HEADER = "## Related Notes"
RELATED_MARKER = "<!-- obsidian-related-notes -->"


def stem_filename(name: str) -> set[str]:
    """Extract meaningful lowercase words from a filename stem."""
    stem = Path(name).stem
    # Strip _2, _3 … collision suffixes
    stem = re.sub(r"_\d+$", "", stem)
    words = re.findall(r"[a-zA-Z]{3,}", stem)
    return {w.lower() for w in words if w.lower() not in STOP}


def keyword_overlap(a: set[str], b: set[str]) -> int:
    return len(a & b)


def already_links_to(content: str, target_stem: str) -> bool:
    """True if the note body already contains [[target_stem]] (case-insensitive)."""
    pattern = re.compile(
        r"\[\[" + re.escape(target_stem) + r"(\|[^\]]+)?\]\]",
        re.IGNORECASE,
    )
    return bool(pattern.search(content))


def build_related_section(links: list[str]) -> str:
    """Format the Related Notes block."""
    items = "\n".join(f"- [[{lnk}]]" for lnk in sorted(links))
    return f"\n\n---\n{RELATED_HEADER}\n{RELATED_MARKER}\n{items}\n"


def update_related_section(content: str, links: list[str]) -> str:
    """
    Replace existing Related Notes block, or append a new one.
    Preserves all other file content unchanged.
    """
    new_block = build_related_section(links)

    # If managed block already present, replace it
    if RELATED_MARKER in content:
        # Remove from the separator line before the header up to end of managed block
        pattern = re.compile(
            r"\n\n---\n" + re.escape(RELATED_HEADER) + r"\n"
            + re.escape(RELATED_MARKER) + r".*",
            re.DOTALL,
        )
        content = pattern.sub("", content)

    return content.rstrip() + new_block


# ─────────────────────────────────────────────────────────────────────────────

def build_link_map(
    md_files: list[Path],
    vault_root: Path,
    max_same: int,
    max_cross: int,
) -> dict[Path, list[str]]:
    """
    For each file, return the list of note names (no .md) it should link to.

    Two-pass:
      Pass 1 — gather metadata (category, keyword set) for every file.
      Pass 2 — for each file, pick same-category + cross-category links.
    """
    # ── Pass 1: metadata ──────────────────────────────────────────────────
    meta: list[dict] = []
    for path in md_files:
        rel = path.relative_to(vault_root)
        # category = immediate parent folder (may be vault root itself)
        category = rel.parent.name if rel.parent != Path(".") else "_root"
        stem = re.sub(r"_\d+$", "", path.stem)   # strip collision suffix
        meta.append({
            "path": path,
            "stem": stem,                           # display name for [[link]]
            "category": category,
            "keywords": stem_filename(path.name),
        })

    # ── Pass 2: link selection ────────────────────────────────────────────
    link_map: dict[Path, list[str]] = {}

    for i, node in enumerate(meta):
        same: list[tuple[int, str]] = []    # (overlap_score, stem)
        cross: list[tuple[int, str]] = []

        for j, other in enumerate(meta):
            if i == j:
                continue
            overlap = keyword_overlap(node["keywords"], other["keywords"])
            if node["category"] == other["category"]:
                # Always include same-category peers (score = 1 at minimum)
                same.append((max(overlap, 1), other["stem"]))
            else:
                if overlap >= 2:   # only cross-link if meaningful overlap
                    cross.append((overlap, other["stem"]))

        # Sort by overlap desc, then alpha for determinism
        same.sort(key=lambda x: (-x[0], x[1]))
        cross.sort(key=lambda x: (-x[0], x[1]))

        chosen = (
            [s for _, s in same[:max_same]]
            + [c for _, c in cross[:max_cross]]
        )
        # Deduplicate while preserving order
        seen: set[str] = set()
        deduped: list[str] = []
        for lnk in chosen:
            if lnk not in seen and lnk != node["stem"]:
                seen.add(lnk)
                deduped.append(lnk)

        link_map[node["path"]] = deduped

    return link_map


def process_vault(
    vault_root: Path,
    max_same: int,
    max_cross: int,
    dry_run: bool,
) -> tuple[int, int]:
    """
    Add/update Related Notes sections for all .md files in vault_root.
    Returns (files_updated, files_skipped).
    """
    md_files = sorted(vault_root.rglob("*.md"))
    if not md_files:
        print(f"  [WARN] No .md files found in {vault_root}")
        return 0, 0

    print(f"\n[{vault_root.name}] {len(md_files)} notes — building link map…")
    link_map = build_link_map(md_files, vault_root, max_same, max_cross)

    updated = skipped = 0
    for path, links in link_map.items():
        if not links:
            skipped += 1
            continue

        content = path.read_text(encoding="utf-8", errors="replace")
        new_content = update_related_section(content, links)

        if new_content == content:
            skipped += 1
            continue

        rel = path.relative_to(vault_root)
        if dry_run:
            print(f"  [DRY-RUN] {rel}  (+{len(links)} links)")
        else:
            path.write_text(new_content, encoding="utf-8")
            print(f"  [UPDATED] {rel}  (+{len(links)} links)")
        updated += 1

    return updated, skipped


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="add_links",
        description="Add Obsidian [[wiki-links]] to notes for better graph connectivity.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
--------
  python add_links.py --dry-run
  python add_links.py
  python add_links.py --roots JoshStrategyWorkVault --max-same 8 --max-cross 4
""",
    )
    parser.add_argument("--roots", nargs="+", metavar="DIR",
                        help="Vault directories to process.")
    parser.add_argument("--config", default="config.yaml",
                        help="config.yaml to read input_roots from.")
    parser.add_argument("--max-same", type=int, default=5, metavar="N",
                        help="Max same-category links per note (default: 5).")
    parser.add_argument("--max-cross", type=int, default=3, metavar="N",
                        help="Max cross-category links per note (default: 3).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing any files.")
    args = parser.parse_args()

    roots = args.roots
    if not roots:
        try:
            import yaml
            cfg = yaml.safe_load(Path(args.config).read_text())
            roots = cfg.get("input_roots", [])
        except Exception:
            print("[ERROR] Could not read config.yaml. Pass --roots explicitly.")
            sys.exit(1)

    if not roots:
        print("[ERROR] No vault roots found.")
        sys.exit(1)

    if args.dry_run:
        print("[INFO] DRY-RUN — no files will be written.\n")

    total_updated = total_skipped = 0
    for root_str in roots:
        root = Path(root_str)
        if not root.exists():
            print(f"[WARN] Vault not found, skipping: {root}")
            continue
        u, s = process_vault(root, args.max_same, args.max_cross, args.dry_run)
        total_updated += u
        total_skipped += s

    print(f"\n── Summary {'(DRY-RUN) ' if args.dry_run else ''}──────────────────────────────")
    print(f"  Notes updated : {total_updated}")
    print(f"  Notes unchanged: {total_skipped}")
    if args.dry_run:
        print("\n  Re-run without --dry-run to write changes.")
    else:
        print("\n[DONE] Open Obsidian and press Ctrl+Shift+G to see the graph.")


if __name__ == "__main__":
    main()
