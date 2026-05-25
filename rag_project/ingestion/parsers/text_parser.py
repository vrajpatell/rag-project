from pathlib import Path

from rag_project.ingestion.parsers.base import BaseParser


class TextParser(BaseParser):
    extensions = (".txt", ".md", ".rst")

    def parse(self, path: Path) -> tuple[str, dict]:
        text = path.read_text(encoding="utf-8", errors="replace")
        return text, {"source_file": str(path)}
