from pathlib import Path

from rag_project.ingestion.parsers.base import BaseParser


class PDFParser(BaseParser):
    extensions = (".pdf",)

    def parse(self, path: Path) -> tuple[str, dict]:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            pages = []
            for i, page in enumerate(reader.pages):
                pages.append(page.extract_text() or "")
            text = "\n\n".join(pages)
            return text, {"source_file": str(path), "format": "pdf", "parser_quality": 0.8}
        except ImportError:
            return (
                f"[PDF parsing unavailable - install pypdf] Placeholder for {path.name}",
                {"source_file": str(path), "format": "pdf", "parser_quality": 0.1},
            )
