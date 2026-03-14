"""
move_files.py
─────────────
Executes the file moves described in classification_plan.json.

Run AFTER classify_notes.py has produced the plan.

Usage
-----
# Preview what would happen (no files touched)
    python move_files.py --dry-run

# Execute moves
    python move_files.py

# Use a different plan or destination
    python move_files.py \\
        --plan classification_output/classification_plan.json \\
        --dest-dir organized_notes

# Skip files whose confidence is below a threshold
    python move_files.py --min-confidence 0.50

Side effects
------------
• Creates destination directories.
• Moves .md files — this is the ONLY script that modifies the filesystem.
• Writes a move_log.json report of everything that was done (or would be done).
• Never deletes files; on filename collision appends a numeric suffix.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def resolve_destination(dest_path: Path) -> Path:
    """
    If *dest_path* already exists, append _2, _3, … until a free name is found.
    Preserves the file suffix.
    """
    if not dest_path.exists():
        return dest_path
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def load_plan(plan_path: Path) -> list[dict]:
    if not plan_path.exists():
        print(f"[ERROR] Plan file not found: {plan_path}")
        print("        Run classify_notes.py first to generate it.")
        sys.exit(1)
    with plan_path.open("r", encoding="utf-8") as fh:
        plan = json.load(fh)
    if not isinstance(plan, list) or not plan:
        print("[ERROR] Plan file is empty or not a JSON array.")
        sys.exit(1)
    return plan


# ──────────────────────────────────────────────────────────────────────────────
# Core move logic
# ──────────────────────────────────────────────────────────────────────────────

def build_move_list(
    plan: list[dict],
    dest_dir: str | None,
    min_confidence: float,
    skip_uncategorized: bool,
) -> list[dict]:
    """
    Resolve every plan entry into a concrete (src, dst) pair.

    Returns a list of move descriptors:
        {
          "original_path":   str,   # source
          "destination_path": str,  # resolved destination (collision-safe)
          "proposed_category": str,
          "confidence":       float,
          "status":           "pending" | "skipped_confidence" | "skipped_uncategorized"
        }
    """
    moves = []
    for entry in plan:
        original = Path(entry["original_path"])
        category = entry["proposed_category"]
        confidence = float(entry.get("confidence", 0.0))
        filename = entry["filename"]

        # ── Skip filters ────────────────────────────────────────────────────
        if skip_uncategorized and category == "Uncategorized":
            moves.append({**entry, "destination_path": None,
                          "status": "skipped_uncategorized"})
            continue
        if confidence < min_confidence:
            moves.append({**entry, "destination_path": None,
                          "status": "skipped_confidence"})
            continue

        # ── Resolve destination path ─────────────────────────────────────────
        if dest_dir:
            # User explicitly overrides the base directory
            dest = Path(dest_dir) / category / filename
        else:
            # Use proposed_new_path from the plan (already includes base dir)
            dest = Path(entry["proposed_new_path"])

        dest = resolve_destination(dest)

        moves.append({
            "original_path": str(original),
            "destination_path": str(dest),
            "proposed_category": category,
            "confidence": confidence,
            "filename": filename,
            "source_root": entry.get("source_root", ""),
            "status": "pending",
        })

    return moves


def execute_moves(moves: list[dict], dry_run: bool) -> list[dict]:
    """
    Perform (or simulate) the moves; update status in-place and return results.
    """
    results = []
    total = sum(1 for m in moves if m["status"] == "pending")
    done = 0

    for m in moves:
        if m["status"] != "pending":
            results.append({**m, "action": "skipped"})
            print(f"[SKIP] {m['status']}: {m['original_path']}")
            continue

        src = Path(m["original_path"])
        dst = Path(m["destination_path"])
        done += 1
        prefix = f"[{done:>4}/{total}]"

        if not src.exists():
            print(f"{prefix} [MISSING] {src}")
            results.append({**m, "status": "error_missing", "action": "none"})
            continue

        if dry_run:
            print(f"{prefix} [DRY-RUN] {src}  →  {dst}")
            results.append({**m, "status": "would_move", "action": "dry_run"})
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print(f"{prefix} [MOVED]   {src}  →  {dst}")
            results.append({**m, "status": "moved", "action": "moved"})

    return results


def write_log(results: list[dict], log_path: Path, dry_run: bool) -> None:
    """Write move_log.json next to the plan."""
    summary = {
        "dry_run": dry_run,
        "total": len(results),
        "moved": sum(1 for r in results if r.get("status") == "moved"),
        "would_move": sum(1 for r in results if r.get("status") == "would_move"),
        "skipped": sum(1 for r in results if "skipped" in r.get("status", "")),
        "errors": sum(1 for r in results if "error" in r.get("status", "")),
    }
    output = {"summary": summary, "entries": results}
    with log_path.open("w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)
    print(f"\n[LOG] {log_path}")


def print_summary(results: list[dict], dry_run: bool) -> None:
    by_category: dict[str, list] = defaultdict(list)
    for r in results:
        by_category[r.get("proposed_category", "?")].append(r)

    label = "DRY-RUN PREVIEW" if dry_run else "MOVE SUMMARY"
    print(f"\n── {label} ─────────────────────────────────────")
    for cat, entries in sorted(by_category.items()):
        moved = sum(1 for e in entries if e.get("status") in ("moved", "would_move"))
        skipped = sum(1 for e in entries if "skipped" in e.get("status", ""))
        errors = sum(1 for e in entries if "error" in e.get("status", ""))
        parts = [f"{moved} file(s)"]
        if skipped:
            parts.append(f"{skipped} skipped")
        if errors:
            parts.append(f"{errors} ERROR")
        print(f"  {cat:<45} {', '.join(parts)}")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="move_files",
        description="Move Markdown files according to classification_plan.json.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
--------
# Preview — no files are touched
  python move_files.py --dry-run

# Execute all moves
  python move_files.py

# Only move files with confidence >= 0.50
  python move_files.py --min-confidence 0.50

# Send everything to a specific directory
  python move_files.py --dest-dir /path/to/organized_notes

# Use a non-default plan file
  python move_files.py --plan classification_output/classification_plan.json
""",
    )
    p.add_argument(
        "--plan",
        default="classification_output/classification_plan.json",
        metavar="PATH",
        help="Path to classification_plan.json (default: classification_output/classification_plan.json).",
    )
    p.add_argument(
        "--dest-dir",
        metavar="DIR",
        default=None,
        help=(
            "Override destination base directory. By default files are moved "
            "within their own vault: <source_root>/<Category>/<filename>. "
            "Only set this if you want to consolidate both vaults into one folder."
        ),
    )
    p.add_argument(
        "--min-confidence",
        type=float,
        default=0.0,
        metavar="FLOAT",
        help="Skip files whose confidence score is below this value (default: 0.0 = move all).",
    )
    p.add_argument(
        "--skip-uncategorized",
        action="store_true",
        help="Do not move files classified as 'Uncategorized'.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview moves without touching any files.",
    )
    p.add_argument(
        "--log-dir",
        metavar="DIR",
        default=None,
        help="Directory for move_log.json (default: same directory as --plan).",
    )
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    plan_path = Path(args.plan)
    log_dir = Path(args.log_dir) if args.log_dir else plan_path.parent

    plan = load_plan(plan_path)
    print(f"[INFO] Loaded {len(plan)} entries from {plan_path}")
    if args.dry_run:
        print("[INFO] DRY-RUN mode — no files will be moved.\n")

    moves = build_move_list(
        plan=plan,
        dest_dir=args.dest_dir,
        min_confidence=args.min_confidence,
        skip_uncategorized=args.skip_uncategorized,
    )

    results = execute_moves(moves, dry_run=args.dry_run)

    log_name = "move_log_dry_run.json" if args.dry_run else "move_log.json"
    write_log(results, log_dir / log_name, dry_run=args.dry_run)
    print_summary(results, dry_run=args.dry_run)

    if args.dry_run:
        print("\n  Re-run without --dry-run to execute the moves.")
    else:
        print("\n[DONE] Files moved.")


if __name__ == "__main__":
    main()
