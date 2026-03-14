"""
model_utils.py
──────────────
Zero-shot classification helpers, adapted from:
    xtremedistil_l6_h256_zeroshot_v1_1_all_33.ipynb

Model: MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33
  • A lightweight NLI-based zero-shot classifier.
  • Multi-label mode is supported but off by default.
  • No fine-tuning required — just supply candidate labels.
"""

from __future__ import annotations

import random
import warnings
from typing import Any

# Silence tokenizer parallelism warnings in subprocess contexts
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def set_seed(seed: int = 42) -> None:
    """Fix random seeds for reproducibility."""
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def load_pipeline(model_name: str) -> Any:
    """
    Load the HuggingFace zero-shot-classification pipeline.

    The model is cached locally by HuggingFace after the first download.
    Subsequent calls load from the local cache — no internet required.
    """
    from transformers import pipeline  # lazy import for faster --help

    print(f"[INFO] Loading model: {model_name}")
    pipe = pipeline(
        "zero-shot-classification",
        model=model_name,
    )
    print("[INFO] Model loaded.")
    return pipe


def classify_text(
    pipe: Any,
    text: str,
    labels: list[str],
    multi_label: bool = False,
    confidence_threshold: float = 0.20,
    fallback_label: str = "Uncategorized",
) -> dict:
    """
    Run zero-shot classification on *text* against *labels*.

    Returns
    -------
    {
        "predicted_category": str,
        "confidence":         float,
        "all_scores":         dict[str, float],   # label → score
    }
    """
    if not text.strip():
        return {
            "predicted_category": fallback_label,
            "confidence": 0.0,
            "all_scores": {lbl: 0.0 for lbl in labels},
        }

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = pipe(text, candidate_labels=labels, multi_label=multi_label)

    # result["labels"] and result["scores"] are parallel lists sorted
    # descending by score (HuggingFace guarantee).
    top_label: str = result["labels"][0]
    top_score: float = float(result["scores"][0])
    all_scores: dict[str, float] = {
        lbl: float(sc) for lbl, sc in zip(result["labels"], result["scores"])
    }

    if top_score < confidence_threshold:
        top_label = fallback_label

    return {
        "predicted_category": top_label,
        "confidence": top_score,
        "all_scores": all_scores,
    }


def classify_batch(
    pipe: Any,
    records: list[dict],
    labels: list[str],
    multi_label: bool = False,
    confidence_threshold: float = 0.20,
    fallback_label: str = "Uncategorized",
) -> list[dict]:
    """
    Classify every record in *records* and return enriched records.

    Each record must have at least:
        "sampled_text", "original_path", "filename", "source_root"

    Added keys per record:
        "predicted_category", "confidence", "all_scores",
        "proposed_new_path"
    """
    total = len(records)
    enriched: list[dict] = []

    for i, rec in enumerate(records, start=1):
        print(f"[{i:>4}/{total}] Classifying: {rec['filename']}")
        result = classify_text(
            pipe,
            rec["sampled_text"],
            labels,
            multi_label=multi_label,
            confidence_threshold=confidence_threshold,
            fallback_label=fallback_label,
        )
        enriched_rec = {**rec, **result}
        # proposed_new_path stays inside the originating vault (source_root)
        enriched_rec["proposed_new_path"] = (
            f"{rec['source_root']}/{result['predicted_category']}/{rec['filename']}"
        )
        enriched.append(enriched_rec)

    return enriched
