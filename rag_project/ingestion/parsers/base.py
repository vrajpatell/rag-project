"""Parser base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BaseParser(ABC):
    extensions: tuple[str, ...] = ()

    @abstractmethod
    def parse(self, path: Path) -> tuple[str, dict]:
        """Return (text, metadata)."""

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions
