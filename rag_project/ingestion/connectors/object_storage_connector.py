"""Object storage connector skeleton."""

from pathlib import Path
from typing import Iterator

from rag_project.ingestion.connectors.base import BaseConnector


class ObjectStorageConnector(BaseConnector):
    def __init__(self, bucket: str, prefix: str = "") -> None:
        self.bucket = bucket
        self.prefix = prefix

    def iter_files(self) -> Iterator[Path]:
        return iter(())
