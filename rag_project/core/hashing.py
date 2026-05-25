"""Hashing utilities for deduplication and cache keys."""

from __future__ import annotations

import hashlib
import re
from typing import Iterable


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_for_hash(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def content_hash(text: str) -> str:
    return sha256_text(normalize_for_hash(text))


class SimHash:
    """Simple SimHash for near-duplicate detection."""

    def __init__(self, bits: int = 64) -> None:
        self.bits = bits

    def fingerprint(self, text: str) -> int:
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return 0
        v = [0] * self.bits
        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            for i in range(self.bits):
                bitmask = 1 << i
                if h & bitmask:
                    v[i] += 1
                else:
                    v[i] -= 1
        fingerprint = 0
        for i in range(self.bits):
            if v[i] > 0:
                fingerprint |= 1 << i
        return fingerprint

    @staticmethod
    def hamming_distance(a: int, b: int) -> int:
        return (a ^ b).bit_count()


def simhash_near_duplicate(a: int, b: int, threshold: int = 5) -> bool:
    return SimHash.hamming_distance(a, b) <= threshold


def cache_key_parts(*parts: Iterable[str] | str) -> str:
    flat: list[str] = []
    for p in parts:
        if isinstance(p, str):
            flat.append(p)
        else:
            flat.extend(str(x) for x in p)
    return sha256_text("|".join(flat))
