"""Screen Bursa Malaysia listed companies via klsescreener.com's screener backend.

The endpoint and form-field names (``min_pe``/``max_pe``,
``min_marketcap``/``max_marketcap``, etc.) were taken from the MIT-licensed
Go scraper https://github.com/kokweikhong/klsescreener-scraper, which
documents the same POST endpoint that klsescreener.com's own screener page
calls. Those still work as documented, confirmed against the live site via
GitHub Actions CI (this sandboxed environment cannot reach klsescreener.com
directly - see .github/workflows/run_screener.yml).

The HTML row layout has moved on from what that reference scraper
documented, though: the live page now has an extra "Change" column (the
absolute change) before "Change %", which shifts every purely
index-based field after it by one - and two more trailing columns
(an indicators cell and an actions cell) that don't matter here. To avoid
silently breaking again the next time the site adds a column, most fields
below are located by each ``<td>``'s ``title`` attribute (e.g.
``title="EPS"``) rather than by raw position; only Price/Change/Change%
share an ambiguous title and are located by their position relative to the
uniquely-titled "Change" cell.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

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


def _cell_by_title(cells: list[Tag], title: str) -> Optional[Tag]:
    for c in cells:
        if c.get("title") == title:
            return c
    return None


def _text_by_title(cells: list[Tag], title: str) -> Optional[str]:
    cell = _cell_by_title(cells, title)
    return clean_text(cell.get_text()) if cell is not None else None


def parse_quote_results(html: str) -> list[Quote]:
    """Parse a klsescreener quote_results response body into Quote rows."""
    soup = BeautifulSoup(html, "lxml")

    quotes: list[Quote] = []
    for row in soup.select("tbody tr.list"):
        cells = row.find_all("td")
        # name, code, category, price, change, change%, 52week, volume,
        # eps, dps, nta, pe, dy, roe, ptbv, market cap = 16 minimum
        if len(cells) < 16:
            continue

        short_name = clean_text(cells[0].get_text()).replace("[s]", "").strip()
        name = cells[0].get("title", "") or short_name
        code = _text_by_title(cells, "Code") or clean_text(cells[1].get_text())

        category, market = "", ""
        category_text = _text_by_title(cells, "Category")
        if category_text:
            if "," in category_text:
                parts = category_text.split(",", 1)
                category, market = parts[0].strip(), parts[1].strip()
            else:
                category = category_text

        # Price, Change, Change% are adjacent and Price/Change% share an
        # ambiguous title, so locate them relative to the unique "Change" cell.
        change_cell = _cell_by_title(cells, "Change")
        change_idx = cells.index(change_cell) if change_cell is not None else 4
        price_text = clean_text(cells[change_idx - 1].get_text()) if change_idx >= 1 else None
        changes_pct_text = clean_text(cells[change_idx + 1].get_text()) if change_idx + 1 < len(cells) else None

        week52_low = week52_high = None
        week52_text = _text_by_title(cells, "52week")
        if week52_text and "-" in week52_text:
            lo, hi = week52_text.split("-", 1)
            week52_low, week52_high = to_float(lo), to_float(hi)

        quotes.append(
            Quote(
                short_name=short_name,
                name=name,
                code=code or "",
                category=category,
                market=market,
                price=to_float(price_text) if price_text else None,
                changes_pct=to_float(changes_pct_text) if changes_pct_text else None,
                week52_low=week52_low,
                week52_high=week52_high,
                volume=to_float(_text_by_title(cells, "Volume") or ""),
                eps=to_float(_text_by_title(cells, "EPS") or ""),
                dps=to_float(_text_by_title(cells, "DPS") or ""),
                nta=to_float(_text_by_title(cells, "NTA") or ""),
                pe=to_float(_text_by_title(cells, "PE") or ""),
                dy=to_float(_text_by_title(cells, "DY") or ""),
                roe=to_float(_text_by_title(cells, "ROE") or ""),
                ptbv=to_float(_text_by_title(cells, "PTBV") or ""),
                market_cap_rm_mil=to_float(_text_by_title(cells, "Market Capital") or ""),
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
