from pathlib import Path
import csv
from typing import Iterable, Dict


def load(path: Path) -> Iterable[Dict]:
    """Placeholder loader for CSV files.

    Args:
        path: Directory containing CSV files.

    Yields:
        A dictionary representing each row and metadata.
    """
    for csv_file in path.glob("*.csv"):
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield {"text": str(row), "metadata": {"source": str(csv_file)}}
