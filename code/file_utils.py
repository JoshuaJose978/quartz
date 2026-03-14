"""
file_utils.py
─────────────
Utilities for discovering and sampling content from Markdown files.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator


# ---------------------------------------------------------------------------
# YAML front-matter pattern (--- ... ---)
# ---------------------------------------------------------------------------
_FRONTMATTER_RE = re.compile(r"^\s*---\s*\n.*?\n---\s*\n", re.DOTALL)


def strip_frontmatter(text: str) -> str:
    """Remove YAML front-matter block if present."""
    return _FRONTMATTER_RE.sub("", text, count=1)


def sample_text(
    text: str,
    max_chars: int = 1500,
    max_lines: int = 0,
    skip_frontmatter: bool = True,
) -> str:
    """
    Return a representative text sample from a Markdown file's content.

    Parameters
    ----------
    text           : Raw file content.
    max_chars      : Hard character limit (0 = disabled).
    max_lines      : Limit by non-empty lines (0 = disabled).
    skip_frontmatter: Strip YAML front-matter before sampling.
    """
    if skip_frontmatter:
        text = strip_frontmatter(text)

    if max_lines > 0:
        lines = [ln for ln in text.splitlines() if ln.strip()]
        text = "\n".join(lines[:max_lines])

    if max_chars > 0:
        text = text[:max_chars]

    return text.strip()


def iter_markdown_files(root: str | Path) -> Iterator[Path]:
    """Yield all *.md files under *root* (recursive)."""
    root = Path(root)
    yield from sorted(root.rglob("*.md"))


def collect_files(
    roots: list[str],
    max_chars: int = 1500,
    max_lines: int = 0,
    skip_frontmatter: bool = True,
) -> list[dict]:
    """
    Walk each root and return a list of records:

        {
            "original_path"  : str,   # relative path from CWD
            "filename"       : str,
            "source_root"    : str,   # which root dir this came from
            "sampled_text"   : str,
        }
    """
    records: list[dict] = []
    for root_str in roots:
        root = Path(root_str)
        if not root.exists():
            print(f"[WARN] Root directory not found, skipping: {root}")
            continue
        for md_path in iter_markdown_files(root):
            try:
                raw = md_path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                print(f"[WARN] Cannot read {md_path}: {exc}")
                continue

            sampled = sample_text(
                raw,
                max_chars=max_chars,
                max_lines=max_lines,
                skip_frontmatter=skip_frontmatter,
            )

            records.append(
                {
                    "original_path": str(md_path),
                    "filename": md_path.name,
                    "source_root": root_str,
                    "sampled_text": sampled,
                }
            )

    return records
