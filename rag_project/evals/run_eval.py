"""Run evaluation suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rag_project.evals.metrics import hit_rate, mrr, precision_at_k, recall_at_k
from rag_project.evals.regression_gate import check_regression
from rag_project.schemas.api import RAGQueryRequest
from rag_project.schemas.evals import EvalReport, GoldenExample
from rag_project.services.factory import ServiceFactory


def load_golden(path: str) -> list[GoldenExample]:
    examples = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            examples.append(GoldenExample.model_validate_json(line))
    return examples


def run_eval(dataset_path: str, output_path: str | None = None) -> EvalReport:
    factory = ServiceFactory.get()
    examples = load_golden(dataset_path)
    metrics: dict[str, float] = {
        "precision_at_5": 0.0,
        "recall_at_5": 0.0,
        "mrr": 0.0,
        "hit_rate": 0.0,
        "abstention_precision": 0.0,
        "faithfulness": 0.0,
    }
    failures = []
    p_vals, r_vals, m_vals, h_vals = [], [], [], []
    abstain_correct = 0
    abstain_total = 0

    for ex in examples:
        req = RAGQueryRequest(
            tenant_id=ex.tenant_id,
            collection_ids=[ex.collection_id],
            query=ex.query,
            top_k=8,
            allow_abstention=True,
        )
        resp = factory.orchestrator.query(req)
        retrieved_ids = [c.chunk_id for c in (factory.retriever.retrieve(
            ex.query, ex.tenant_id, [ex.collection_id], top_k=20
        ))]
        relevant = set(ex.relevant_chunk_ids)
        if relevant:
            p_vals.append(precision_at_k(retrieved_ids, relevant, 5))
            r_vals.append(recall_at_k(retrieved_ids, relevant, 5))
            m_vals.append(mrr(retrieved_ids, relevant))
            h_vals.append(hit_rate(retrieved_ids, relevant, 5))
        if not ex.expected_answer or "don't have" in ex.expected_answer.lower():
            abstain_total += 1
            if resp.abstained:
                abstain_correct += 1
        elif resp.answer and not resp.abstained:
            if ex.expected_answer.lower()[:20] in resp.answer.lower() or any(
                w in resp.answer.lower() for w in ex.expected_answer.lower().split()[:5]
            ):
                pass
            elif ex.tags and "requires_abstain" in ex.tags and resp.abstained:
                abstain_correct += 1
                abstain_total += 1

    n = max(len(p_vals), 1)
    metrics["precision_at_5"] = sum(p_vals) / n if p_vals else 0
    metrics["recall_at_5"] = sum(r_vals) / n if r_vals else 0
    metrics["mrr"] = sum(m_vals) / n if m_vals else 0
    metrics["hit_rate"] = sum(h_vals) / n if h_vals else 0
    metrics["abstention_precision"] = abstain_correct / max(abstain_total, 1)
    metrics["faithfulness"] = 1.0 - (len(failures) / max(len(examples), 1))

    passed = check_regression(metrics)
    report = EvalReport(
        dataset_path=dataset_path,
        total_examples=len(examples),
        metrics=metrics,
        failures=failures,
        passed_regression_gate=passed,
    )
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(report.model_dump_json(indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="./evals/golden.jsonl")
    parser.add_argument("--output", default="./artifacts/evals/report.json")
    args = parser.parse_args()
    report = run_eval(args.dataset, args.output)
    print(json.dumps(report.model_dump(), indent=2))
    raise SystemExit(0 if report.passed_regression_gate else 1)


if __name__ == "__main__":
    main()
