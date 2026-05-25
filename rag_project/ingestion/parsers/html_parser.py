from pathlib import Path

from rag_project.ingestion.normalizer import normalize_text
from rag_project.ingestion.parsers.base import BaseParser


class HTMLParser(BaseParser):
    extensions = (".html", ".htm")

    def parse(self, path: Path) -> tuple[str, dict]:
        raw = path.read_text(encoding="utf-8", errors="replace")
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(raw, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            text = soup.get_text(separator=" ")
        except ImportError:
            text = normalize_text(raw, strip_html=True)
        return normalize_text(text), {"source_file": str(path), "format": "html"}
