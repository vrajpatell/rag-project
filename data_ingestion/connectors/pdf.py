from pathlib import Path
from typing import Iterable, Dict


def load(path: Path) -> Iterable[Dict]:
    """Placeholder loader for PDF files.

    Args:
        path: Path to a directory containing PDF files.

    Yields:
        A dictionary with at least the keys `text` and `metadata`.
    """
    # TODO: implement PDF parsing and text extraction
    for pdf_file in path.glob("*.pdf"):
        yield {
            "text": f"Dummy content from {pdf_file.name}",
            "metadata": {"source": str(pdf_file)},
        }
