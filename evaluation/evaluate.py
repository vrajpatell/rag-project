#!/usr/bin/env python
"""Evaluate the performance of the RAG system."""

import argparse
from pathlib import Path
import json

from .metrics import precision_at_k, mean_reciprocal_rank


def evaluate(results_jsonl: Path, report_path: Path) -> None:
    """Compute simple metrics over a JSONL file of RAG responses."""
    queries = []
    relevances = []
    with results_jsonl.open() as f:
        for line in f:
            data = json.loads(line)
            queries.append(data["query"])
            # In a real system, relevance judgments would be more sophisticated
            relevances.append([1] * len(data["retrieved_contexts"]))
    p5 = precision_at_k(relevances, k=5)
    mrr = mean_reciprocal_rank(relevances)
    report = {
        "precision@5": p5,
        "mrr": mrr,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RAG responses.")
    parser.add_argument(
        "--results",
        default="artifacts/eval/rag_results.jsonl",
        help="Path to results JSONL",
    )
    parser.add_argument(
        "--report", default="artifacts/eval/report.json", help="Output report JSON"
    )
    args = parser.parse_args()
    evaluate(Path(args.results), Path(args.report))
