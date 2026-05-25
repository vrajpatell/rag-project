from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator


class BaseConnector(ABC):
    @abstractmethod
    def iter_files(self) -> Iterator[Path]:
        ...
