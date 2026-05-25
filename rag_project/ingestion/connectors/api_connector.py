"""API connector skeleton."""

from pathlib import Path
from typing import Iterator

from rag_project.ingestion.connectors.base import BaseConnector


class APIConnector(BaseConnector):
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def iter_files(self) -> Iterator[Path]:
        return iter(())
