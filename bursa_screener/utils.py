"""Shared parsing helpers used across the screener modules."""
from __future__ import annotations

import re
from typing import Optional

_SPACES = re.compile(r"\s+")

# klsescreener.com and i3investor.com both reject requests without a
# browser-like User-Agent.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}


def clean_text(text: str) -> str:
    return _SPACES.sub(" ", text).strip()


def to_float(text: str) -> Optional[float]:
    text = text.replace(",", "").replace("%", "").strip()
    if not text or text.lower() in {"-", "n/a"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None
