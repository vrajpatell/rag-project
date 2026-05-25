from pathlib import Path
from typing import Iterator

from rag_project.ingestion.connectors.base import BaseConnector


class LocalConnector(BaseConnector):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def iter_files(self) -> Iterator[Path]:
        if not self.root.exists():
            return
        for path in sorted(self.root.rglob("*")):
            if path.is_file() and not path.name.startswith("."):
                yield path
