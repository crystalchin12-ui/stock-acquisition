"""Best-effort lookup of substantial (>=5%) shareholders for a Bursa Malaysia
counter, via i3investor's substantial-shareholder disclosure page.

IMPORTANT CAVEATS
------------------
i3investor's page is a *transaction log* of Section 137/138 disclosures
(acquisitions, disposals, notices of interest) rather than a clean, current
cap table. This module takes, per shareholder name, the most recently
disclosed "Total %" figure as an estimate of their current holding. That
estimate is only as fresh and complete as the company's latest disclosure -
it can miss recent private placements, conversions, or holdings that never
crossed a disclosure threshold change.

Before treating any candidate as a real acquisition target, confirm the
shareholding manually against the company's latest Annual Report ("Analysis
of Shareholdings" section) or a fresh Bursa LINK announcement.

This module could not be exercised against the live site from within the
sandboxed environment that authored it (klse.i3investor.com is not
reachable from that network's egress proxy), so the CSS/column-matching
logic below is unverified against real HTML. It is written defensively:
on any parsing failure it returns an empty result rather than raising, so
callers should always fall back to the manual-check URL from source_url().
Verify the column matching still works on the first live run and adjust
COLUMN_KEYWORDS below if the site's headers have changed.
"""
from __future__ import annotations

from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from .utils import HEADERS, to_float

SUBSTANTIAL_SHAREHOLDER_URL = "https://klse.i3investor.com/web/stock/substantial-shareholder/{code}"

# Header keywords used to locate the relevant columns regardless of exact
# wording/ordering on the live page.
COLUMN_KEYWORDS = {
    "name": ("name",),
    "total": ("total", "%"),
    "date": ("date",),
}


def source_url(code: str) -> str:
    return SUBSTANTIAL_SHAREHOLDER_URL.format(code=code)


@dataclass
class ShareholderEstimate:
    name: str
    total_pct: float
    as_of: str


def _find_column(headers: list[str], keywords: tuple[str, ...]) -> int:
    for i, h in enumerate(headers):
        if all(k in h for k in keywords):
            return i
    return -1


def get_latest_substantial_shareholders(code: str, *, timeout: float = 30) -> list[ShareholderEstimate]:
    """Return each disclosed substantial shareholder's most recent Total %.

    Returns an empty list (never raises) on any network or parsing failure
    so callers can fall back to manual review via source_url(code).
    """
    try:
        resp = requests.get(source_url(code), headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    try:
        soup = BeautifulSoup(resp.text, "lxml")
        table = soup.find("table")
        if table is None:
            return []

        header_cells = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        name_idx = _find_column(header_cells, COLUMN_KEYWORDS["name"])
        total_idx = _find_column(header_cells, COLUMN_KEYWORDS["total"])
        date_idx = _find_column(header_cells, COLUMN_KEYWORDS["date"])
        if name_idx < 0 or total_idx < 0:
            return []

        latest: dict[str, ShareholderEstimate] = {}
        for row in table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cells) <= max(name_idx, total_idx):
                continue
            name = cells[name_idx].strip()
            pct = to_float(cells[total_idx])
            as_of = cells[date_idx].strip() if 0 <= date_idx < len(cells) else ""
            if not name or pct is None:
                continue
            # Rows are assumed newest-first; keep only the first (latest) per name.
            latest.setdefault(name, ShareholderEstimate(name=name, total_pct=pct, as_of=as_of))

        return list(latest.values())
    except Exception:
        return []


def has_majority_shareholder(code: str, threshold: float = 50.0) -> tuple[bool, list[ShareholderEstimate]]:
    holders = get_latest_substantial_shareholders(code)
    majority = [h for h in holders if h.total_pct >= threshold]
    return (len(majority) > 0, holders)
