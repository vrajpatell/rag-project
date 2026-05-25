import re


def preprocess_query(query: str) -> str:
    q = query.strip()
    q = re.sub(r"\s+", " ", q)
    return q
