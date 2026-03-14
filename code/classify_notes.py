"""
classify_notes.py
─────────────────
CLI entry-point for the zero-shot Markdown classification pipeline.

Usage (minimal):
    python classify_notes.py

Usage (with overrides):
    python classify_notes.py \\
        --config config.yaml \\
        --roots idc_ai_engineering_markdown_docs JoshStrategyWorkVault \\
        --output-dir classification_output \\
        --labels-file labels.yaml

Full help:
    python classify_notes.py --help

Side effects:
    • Reads .md files (never modifies them).
    • Writes classification_output/classification_plan.json
    • Writes classification_output/classification_plan.csv
    • Writes classification_output/link_suggestions.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import yaml  # pip install pyyaml


# ──────────────────────────────────────────────────────────────────────────────
# Config helpers
# ──────────────────────────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    p = Path(config_path)
    if not p.exists():
        print(f"[ERROR] Config file not found: {p}")
        sys.exit(1)
    with p.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return cfg


def merge_cli_overrides(cfg: dict, args: argparse.Namespace) -> dict:
    """CLI flags override config-file values."""
    if args.roots:
        cfg["input_roots"] = args.roots
    if args.output_dir:
        cfg["output_dir"] = args.output_dir
    if args.model:
        cfg["model_name"] = args.model
    if args.labels_file:
        lp = Path(args.labels_file)
        if not lp.exists():
            print(f"[ERROR] Labels file not found: {lp}")
            sys.exit(1)
        with lp.open("r", encoding="utf-8") as fh:
            label_data = yaml.safe_load(fh)
        if isinstance(label_data, list):
            cfg["labels"] = label_data
        elif isinstance(label_data, dict) and "labels" in label_data:
            cfg["labels"] = label_data["labels"]
        else:
            print("[ERROR] labels-file must be a YAML list or dict with 'labels' key.")
            sys.exit(1)
    if args.threshold is not None:
        cfg["confidence_threshold"] = args.threshold
    if args.max_chars is not None:
        cfg["max_chars"] = args.max_chars
    return cfg


# ──────────────────────────────────────────────────────────────────────────────
# Artifact writers
# ──────────────────────────────────────────────────────────────────────────────

def write_classification_plan(records: list[dict], output_dir: Path) -> None:
    """Write classification_plan.json and classification_plan.csv.

    proposed_new_path is always inside the originating vault:
        <source_root>/<Category>/<filename>
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build clean export records (exclude sampled_text and all_scores verbosity)
    export = []
    for r in records:
        # proposed_new_path was already set vault-relative in classify_batch
        export.append(
            {
                "original_path": r["original_path"],
                "filename": r["filename"],
                "proposed_category": r["predicted_category"],
                "proposed_new_path": r["proposed_new_path"],
                "confidence": round(r["confidence"], 4),
                "source_root": r["source_root"],
            }
        )

    # JSON
    json_path = output_dir / "classification_plan.json"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(export, fh, indent=2, ensure_ascii=False)
    print(f"[OUT] {json_path}")

    # CSV
    csv_path = output_dir / "classification_plan.csv"
    fieldnames = [
        "original_path",
        "filename",
        "proposed_category",
        "proposed_new_path",
        "confidence",
        "source_root",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(export)
    print(f"[OUT] {csv_path}")


def write_link_suggestions(
    records: list[dict],
    output_dir: Path,
    max_suggestions: int = 5,
) -> None:
    """
    For each file, suggest links to other files in the same predicted category.

    Output: link_suggestions.json  — list of objects:
        {
          "file": "ProposedFolderName/file.md",
          "source_root": "...",
          "proposed_category": "...",
          "add_links_to": ["ProposedFolderName/other.md", ...]
        }
    """
    # Group by predicted category
    by_category: dict[str, list[dict]] = {}
    for r in records:
        cat = r["predicted_category"]
        by_category.setdefault(cat, []).append(r)

    suggestions = []
    for r in records:
        cat = r["predicted_category"]
        peers = [
            p["proposed_new_path"]
            for p in by_category.get(cat, [])
            if p["original_path"] != r["original_path"]
        ]
        # Sort deterministically (alphabetical) then cap
        peers = sorted(peers)[:max_suggestions]

        suggestions.append(
            {
                "file": r["proposed_new_path"],
                "source_root": r["source_root"],
                "proposed_category": cat,
                "add_links_to": peers,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "link_suggestions.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(suggestions, fh, indent=2, ensure_ascii=False)
    print(f"[OUT] {out_path}")


def write_scores_detail(records: list[dict], output_dir: Path) -> None:
    """Write all_scores_detail.json for debugging / inspection."""
    detail = []
    for r in records:
        detail.append(
            {
                "original_path": r["original_path"],
                "filename": r["filename"],
                "predicted_category": r["predicted_category"],
                "confidence": round(r["confidence"], 4),
                "all_scores": {k: round(v, 4) for k, v in r.get("all_scores", {}).items()},
            }
        )
    out_path = output_dir / "all_scores_detail.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(detail, fh, indent=2, ensure_ascii=False)
    print(f"[OUT] {out_path}")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="classify_notes",
        description="Zero-shot classify Markdown notes and produce reorganisation plan.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
--------
# Use defaults from config.yaml
  python classify_notes.py

# Override root dirs and output path
  python classify_notes.py \\
      --roots idc_ai_engineering_markdown_docs JoshStrategyWorkVault \\
      --output-dir out/

# Use a custom label file and lower confidence threshold
  python classify_notes.py --labels-file my_labels.yaml --threshold 0.15

# Dry run: only collect files, skip classification
  python classify_notes.py --dry-run
""",
    )
    p.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML config file (default: config.yaml).",
    )
    p.add_argument(
        "--roots",
        nargs="+",
        metavar="DIR",
        help="Override input root directories.",
    )
    p.add_argument(
        "--output-dir",
        metavar="DIR",
        help="Override output directory for artifacts.",
    )
    p.add_argument(
        "--model",
        metavar="MODEL_NAME",
        help="Override HuggingFace model name/path.",
    )
    p.add_argument(
        "--labels-file",
        metavar="PATH",
        help="YAML file containing a list of category labels.",
    )
    p.add_argument(
        "--threshold",
        type=float,
        metavar="FLOAT",
        help="Override confidence threshold (0–1).",
    )
    p.add_argument(
        "--max-chars",
        type=int,
        metavar="N",
        help="Override maximum characters sampled per file.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and sample files only; skip model classification.",
    )
    p.add_argument(
        "--no-scores-detail",
        action="store_true",
        help="Skip writing all_scores_detail.json.",
    )
    return p


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # ── Load and merge config ──────────────────────────────────────────────
    cfg = load_config(args.config)
    cfg = merge_cli_overrides(cfg, args)

    model_name: str = cfg.get("model_name", "MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33")
    input_roots: list[str] = cfg.get("input_roots", [])
    output_dir = Path(cfg.get("output_dir", "classification_output"))
    labels: list[str] = cfg.get("labels", [])
    multi_label: bool = bool(cfg.get("multi_label", False))
    confidence_threshold: float = float(cfg.get("confidence_threshold", 0.20))
    max_chars: int = int(cfg.get("max_chars", 1500))
    max_lines: int = int(cfg.get("max_lines", 0))
    skip_frontmatter: bool = bool(cfg.get("skip_frontmatter", True))
    random_seed: int = int(cfg.get("random_seed", 42))
    max_link_suggestions: int = int(cfg.get("max_link_suggestions", 5))

    if not input_roots:
        print("[ERROR] No input_roots specified in config or CLI.")
        sys.exit(1)
    if not labels:
        print("[ERROR] No labels specified. Edit config.yaml or pass --labels-file.")
        sys.exit(1)

    # ── Reproducibility seed ───────────────────────────────────────────────
    from model_utils import set_seed
    set_seed(random_seed)

    # ── File discovery & sampling ──────────────────────────────────────────
    from file_utils import collect_files
    print(f"[INFO] Scanning roots: {input_roots}")
    records = collect_files(
        roots=input_roots,
        max_chars=max_chars,
        max_lines=max_lines,
        skip_frontmatter=skip_frontmatter,
    )
    print(f"[INFO] Found {len(records)} Markdown files.")

    if args.dry_run:
        print("[DRY-RUN] Skipping classification. Writing file list only.")
        output_dir.mkdir(parents=True, exist_ok=True)
        dry_out = output_dir / "discovered_files.json"
        with dry_out.open("w", encoding="utf-8") as fh:
            json.dump(
                [{"original_path": r["original_path"], "filename": r["filename"],
                  "source_root": r["source_root"],
                  "sampled_chars": len(r["sampled_text"])} for r in records],
                fh, indent=2, ensure_ascii=False,
            )
        print(f"[OUT] {dry_out}")
        return

    # ── Classification ─────────────────────────────────────────────────────
    from model_utils import load_pipeline, classify_batch
    pipe = load_pipeline(model_name)

    enriched = classify_batch(
        pipe=pipe,
        records=records,
        labels=labels,
        multi_label=multi_label,
        confidence_threshold=confidence_threshold,
    )

    # ── Write artifacts ────────────────────────────────────────────────────
    write_classification_plan(enriched, output_dir)
    write_link_suggestions(enriched, output_dir, max_suggestions=max_link_suggestions)
    if not args.no_scores_detail:
        write_scores_detail(enriched, output_dir)

    # ── Summary ───────────────────────────────────────────────────────────
    from collections import Counter
    counts = Counter(r["predicted_category"] for r in enriched)
    print("\n── Category summary ──────────────────────────────")
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {n:>4}  {cat}")
    print(f"\n[DONE] Artifacts written to: {output_dir}/")


if __name__ == "__main__":
    main()
