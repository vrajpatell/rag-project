#!/usr/bin/env python
"""Generate synthetic Question–Context–Answer triples from RAG results."""

from pathlib import Path
import json


def synthesize(input_jsonl: Path, output_jsonl: Path) -> None:
    """Placeholder for synthesising QCA triples."""
    # TODO: implement realistic synthesis using language models
    triples = []
    if input_jsonl.exists():
        for line in input_jsonl.read_text().splitlines():
            data = json.loads(line)
            triples.append(
                {
                    "question": data["query"],
                    "context": "\n".join([ctx["text"] for ctx in data["retrieved_contexts"]]),
                    "answer": data["synthesized_answer"],
                }
            )
    output_jsonl.write_text("\n".join(json.dumps(t) for t in triples))


if __name__ == "__main__":
    input_file = Path("artifacts/synthetic/rag_results.jsonl")
    output_file = Path("artifacts/synthetic/qca_triples.jsonl")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    synthesize(input_file, output_file)