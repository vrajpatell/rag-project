#!/usr/bin/env python
"""Fine‑tune a base model using LoRA or QLoRA."""

import argparse
from pathlib import Path


def finetune(dataset_path: Path, base_model: str, output_dir: Path) -> None:
    """Placeholder for fine‑tuning logic.

    Args:
        dataset_path: Path to JSONL file with QCA triples.
        base_model: Identifier of the pre‑trained model.
        output_dir: Directory to write adapter weights.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    # TODO: implement LoRA/QLoRA fine‑tuning
    (output_dir / "adapter.bin").write_bytes(b"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine‑tune using LoRA/QLoRA.")
    parser.add_argument("--dataset", default="artifacts/synthetic/qca_triples.jsonl", help="Path to QCA dataset")
    parser.add_argument("--base-model", default="meta-llama/Meta-Llama-3-8B", help="Base model identifier")
    parser.add_argument("--output", default="artifacts/models", help="Output directory for adapters")
    args = parser.parse_args()
    finetune(Path(args.dataset), args.base_model, Path(args.output))