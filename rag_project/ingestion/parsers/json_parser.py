import json
from pathlib import Path

from rag_project.ingestion.parsers.base import BaseParser


class JSONParser(BaseParser):
    extensions = (".json",)

    def parse(self, path: Path) -> tuple[str, dict]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            text = "\n".join(f"{k}: {v}" for k, v in data.items())
        elif isinstance(data, list):
            text = json.dumps(data, indent=2)
        else:
            text = str(data)
        return text, {"source_file": str(path), "format": "json"}
