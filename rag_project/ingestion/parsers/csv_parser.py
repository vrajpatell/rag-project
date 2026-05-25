import csv
from pathlib import Path

from rag_project.ingestion.parsers.base import BaseParser


class CSVParser(BaseParser):
    extensions = (".csv",)

    def parse(self, path: Path) -> tuple[str, dict]:
        rows: list[str] = []
        with path.open(encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                rows.append(f"Row {i}: " + " | ".join(f"{k}={v}" for k, v in row.items()))
        return "\n".join(rows), {"source_file": str(path), "format": "csv"}
