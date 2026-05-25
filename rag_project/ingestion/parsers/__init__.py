from pathlib import Path

from rag_project.ingestion.parsers.csv_parser import CSVParser
from rag_project.ingestion.parsers.docx_parser import DocxParser
from rag_project.ingestion.parsers.html_parser import HTMLParser
from rag_project.ingestion.parsers.json_parser import JSONParser
from rag_project.ingestion.parsers.pdf_parser import PDFParser
from rag_project.ingestion.parsers.text_parser import TextParser

PARSERS = [TextParser(), HTMLParser(), CSVParser(), JSONParser(), PDFParser(), DocxParser()]


def get_parser(path: Path):
    for p in PARSERS:
        if p.supports(path):
            return p
    return TextParser()
