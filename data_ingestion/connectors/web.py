from typing import Iterable, Dict, List


def load(urls: List[str]) -> Iterable[Dict]:
    """Placeholder loader for web pages.

    Args:
        urls: A list of URLs to fetch.

    Yields:
        A dictionary with page content and metadata.
    """
    # TODO: implement web scraping
    for url in urls:
        yield {
            "text": f"Content scraped from {url}",
            "metadata": {"source": url},
        }
