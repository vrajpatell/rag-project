"""Web connector skeleton."""

from pathlib import Path
from typing import Iterator

from rag_project.ingestion.connectors.base import BaseConnector


class WebConnector(BaseConnector):
    def __init__(self, url: str) -> None:
        self.url = url

    def iter_files(self) -> Iterator[Path]:
        # Production: fetch URL, save to temp file
        return iter(())
