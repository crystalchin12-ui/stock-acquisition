"""Screen Bursa Malaysia listed companies via klsescreener.com's screener backend.

The endpoint and form-field names below (``min_pe``/``max_pe``,
``min_marketcap``/``max_marketcap``, etc.) and the HTML row layout
(``tbody tr.list`` -> 15 ``td`` cells in a fixed order) were taken from the
MIT-licensed Go scraper https://github.com/kokweikhong/klsescreener-scraper,
which documents the same POST endpoint that klsescreener.com's own screener
page calls. This module is an independent Python port, not a copy of that
code.

Note: this could not be exercised against the live site from within the
sandboxed environment that authored it (klsescreener.com is not reachable
from that network's egress proxy). The HTML-parsing logic is covered by an
offline unit test using a synthetic row (see tests/), but you should sanity
check the first live run's output against https://www.klsescreener.com/v2/screener
manually before relying on it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .utils import HEADERS, clean_text, to_float

BASE_URL = "https://www.klsescreener.com"
QUOTE_RESULTS_URL = f"{BASE_URL}/v2/screener/quote_results"

REQUEST_HEADERS = {
    **HEADERS,
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}


@dataclass
class Quote:
    short_name: str
    name: str
    code: str
    category: str
    market: str
    price: Optional[float]
    changes_pct: Optional[float]
    week52_low: Optional[float]
    week52_high: Optional[float]
    volume: Optional[float]
    eps: Optional[float]
    dps: Optional[float]
    nta: Optional[float]
    pe: Optional[float]
    dy: Optional[float]
    roe: Optional[float]
    ptbv: Optional[float]
    market_cap_rm_mil: Optional[float]


def parse_quote_results(html: str) -> list[Quote]:
    """Parse a klsescreener quote_results response body into Quote rows."""
    soup = BeautifulSoup(html, "lxml")

    quotes: list[Quote] = []
    for row in soup.select("tbody tr.list"):
        cells = row.find_all("td")
        if len(cells) < 15:
            continue
        cell_text = [clean_text(c.get_text()) for c in cells]

        short_name = cell_text[0].replace("[s]", "").strip()
        name = cells[0].get("title", "") or short_name
        code = cell_text[1]

        market, category = "", ""
        if "," in cell_text[2]:
            parts = cell_text[2].split(",", 1)
            category, market = parts[0].strip(), parts[1].strip()

        week52_low = week52_high = None
        if "-" in cell_text[5]:
            lo, hi = cell_text[5].split("-", 1)
            week52_low, week52_high = to_float(lo), to_float(hi)

        quotes.append(
            Quote(
                short_name=short_name,
                name=name,
                code=code,
                category=category,
                market=market,
                price=to_float(cell_text[3]),
                changes_pct=to_float(cell_text[4]),
                week52_low=week52_low,
                week52_high=week52_high,
                volume=to_float(cell_text[6]),
                eps=to_float(cell_text[7]),
                dps=to_float(cell_text[8]),
                nta=to_float(cell_text[9]),
                pe=to_float(cell_text[10]),
                dy=to_float(cell_text[11]),
                roe=to_float(cell_text[12]),
                ptbv=to_float(cell_text[13]),
                market_cap_rm_mil=to_float(cell_text[14]),
            )
        )
    return quotes


def fetch_quotes(
    *,
    max_pe: Optional[float] = None,
    min_pe: Optional[float] = None,
    max_marketcap: Optional[float] = None,
    min_marketcap: Optional[float] = None,
    board: Optional[int] = None,
    timeout: float = 30,
) -> list[Quote]:
    """Query klsescreener.com's screener and return matching rows.

    max_marketcap / min_marketcap are in RM millions, matching the site's
    own "Market Cap (mil)" column.
    """
    payload = {"getquote": "1"}
    if min_pe is not None:
        payload["min_pe"] = str(min_pe)
    if max_pe is not None:
        payload["max_pe"] = str(max_pe)
    if min_marketcap is not None:
        payload["min_marketcap"] = str(min_marketcap)
    if max_marketcap is not None:
        payload["max_marketcap"] = str(max_marketcap)
    if board is not None:
        payload["board"] = str(board)

    resp = requests.post(QUOTE_RESULTS_URL, data=payload, headers=REQUEST_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return parse_quote_results(resp.text)
