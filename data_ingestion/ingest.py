#!/usr/bin/env python
"""Ingest data from various connectors and write into the raw data directory."""

import argparse
from pathlib import Path
from typing import Iterable, Dict

from .connectors import pdf, web, api, csv as csv_loader


def ingest(source: str, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    # Dummy implementation: call connectors based on source type
    docs: Iterable[Dict] = []
    path = Path(source)
    if path.is_dir():
        # Determine file types present
        if any(f.suffix == ".pdf" for f in path.iterdir()):
            docs = pdf.load(path)
        elif any(f.suffix == ".csv" for f in path.iterdir()):
            docs = csv_loader.load(path)
    elif source.startswith("http"):
        docs = web.load([source])
    else:
        docs = api.load(source)
    # Write to destination as simple text files
    for i, doc in enumerate(docs):
        outfile = destination / f"doc_{i}.txt"
        outfile.write_text(doc["text"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into raw data directory.")
    parser.add_argument("--source", required=True, help="Path or URL to ingest from")
    parser.add_argument("--output", default="data/raw", help="Output directory for raw documents")
    args = parser.parse_args()
    ingest(args.source, Path(args.output))