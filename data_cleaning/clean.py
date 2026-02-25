#!/usr/bin/env python
"""Clean raw documents according to rules defined in ruleset.yaml."""

import argparse
from pathlib import Path
from typing import Iterable, Dict
import yaml

from .ner_srl import enrich_entities


def read_raw(input_dir: Path) -> Iterable[Dict]:
    for f in input_dir.glob("*.txt"):
        yield {"text": f.read_text(), "metadata": {"source": str(f)}}


def clean_text(text: str, rules: dict) -> str:
    cleaned = text
    if rules.get("remove_control_chars", True):
        cleaned = "".join(ch for ch in cleaned if ch.isprintable() or ch.isspace())
    # TODO: implement HTML stripping, language detection, deduplication, etc.
    return cleaned


def write_clean(docs: Iterable[Dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for i, doc in enumerate(docs):
        path = output_dir / f"clean_{i}.txt"
        path.write_text(doc["text"])


def main(input_dir: Path, output_dir: Path, rules_file: Path) -> None:
    rules = yaml.safe_load(rules_file.read_text())
    cleaned_docs = []
    for doc in read_raw(input_dir):
        text = clean_text(doc["text"], rules)
        enriched = enrich_entities(text)
        cleaned_docs.append({"text": enriched, "metadata": doc["metadata"]})
    write_clean(cleaned_docs, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean raw documents.")
    parser.add_argument(
        "--input", default="data/raw", help="Directory containing raw text files"
    )
    parser.add_argument(
        "--output", default="data/clean", help="Directory to write cleaned files"
    )
    parser.add_argument(
        "--rules",
        default="data_cleaning/ruleset.yaml",
        help="YAML file with cleaning rules",
    )
    args = parser.parse_args()
    main(Path(args.input), Path(args.output), Path(args.rules))
