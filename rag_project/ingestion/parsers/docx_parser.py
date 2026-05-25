from pathlib import Path

from rag_project.ingestion.parsers.base import BaseParser


class DocxParser(BaseParser):
    extensions = (".docx",)

    def parse(self, path: Path) -> tuple[str, dict]:
        try:
            from docx import Document

            doc = Document(str(path))
            text = "\n".join(p.text for p in doc.paragraphs if p.text)
            return text, {"source_file": str(path), "format": "docx", "parser_quality": 0.85}
        except ImportError:
            return (
                f"[DOCX parsing unavailable - install python-docx] Placeholder for {path.name}",
                {"source_file": str(path), "format": "docx", "parser_quality": 0.1},
            )
