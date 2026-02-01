from typing import Iterable, Dict, Any


def load(endpoint: str, params: dict | None = None) -> Iterable[Dict[str, Any]]:
    """Placeholder loader for REST APIs.

    Args:
        endpoint: Base URL of the API.
        params: Query parameters for the API request.

    Yields:
        A dictionary with API response data and metadata.
    """
    # TODO: implement API fetching
    yield {"text": f"Response from {endpoint}", "metadata": {"params": params or {}}}
