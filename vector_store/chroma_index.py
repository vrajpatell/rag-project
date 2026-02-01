from typing import Any


class ChromaIndex:
    """Placeholder for a Chroma index implementation."""

    def __init__(self, collection_name: str) -> None:
        self.collection_name = collection_name
        # TODO: initialise Chroma client

    def search(self, query: str, top_k: int = 8) -> Any:
        # TODO: implement search using Chroma
        raise NotImplementedError