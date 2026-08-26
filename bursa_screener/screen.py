"""End-to-end acquisition-candidate screen for Bursa Malaysia listed companies:

  1. net loss              (EPS < 0)
  2. negative PE            (PE < 0 - follows automatically from #1 since
                              price is always positive)
  3. market cap < RM50 million
  4. a single shareholder holding more than 50% of shares

Stage 1 (financials) queries klsescreener.com directly - see klse_screener.py.
Stage 2 (shareholding) is a best-effort check against i3investor's
substantial-shareholder disclosures - see shareholder.py for important
caveats. Always confirm shareholding manually before acting on a candidate.

Usage:
    python -m bursa_screener.screen --out candidates.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
import time

from .klse_screener import fetch_quotes
from .shareholder import has_majority_shareholder, source_url


def run(
    max_marketcap: float = 50.0,
    threshold: float = 50.0,
    delay: float = 1.0,
    out_path: str = "candidates.csv",
) -> None:
    print(
        f"Stage 1: querying klsescreener.com for market cap < RM{max_marketcap}m, negative PE ...",
        file=sys.stderr,
    )
    quotes = fetch_quotes(max_pe=-0.01, max_marketcap=max_marketcap)
    # Belt-and-suspenders: only keep genuine net-loss rows (EPS < 0 too),
    # in case the site's PE field is blank/zero for some loss-making rows.
    candidates = [q for q in quotes if q.pe is not None and q.pe < 0 and q.eps is not None and q.eps < 0]
    print(f"  -> {len(candidates)} counters meet the financial criteria", file=sys.stderr)

    rows = []
    print(
        f"Stage 2: checking substantial shareholders on i3investor (threshold {threshold}%) ...",
        file=sys.stderr,
    )
    for q in candidates:
        has_majority, holders = has_majority_shareholder(q.code, threshold=threshold)
        top = max(holders, key=lambda h: h.total_pct, default=None)
        rows.append(
            {
                "code": q.code,
                "name": q.name,
                "market": q.market,
                "price": q.price,
                "eps": q.eps,
                "pe": q.pe,
                "market_cap_rm_mil": q.market_cap_rm_mil,
                "top_shareholder": top.name if top else "",
                "top_shareholder_pct": top.total_pct if top else "",
                "has_majority_shareholder": has_majority,
                "verify_shareholding_url": source_url(q.code),
            }
        )
        time.sleep(delay)

    fieldnames = list(rows[0].keys()) if rows else [
        "code", "name", "market", "price", "eps", "pe", "market_cap_rm_mil",
        "top_shareholder", "top_shareholder_pct", "has_majority_shareholder",
        "verify_shareholding_url",
    ]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    matches = [r for r in rows if r["has_majority_shareholder"]]
    print(
        f"Done. {len(matches)}/{len(rows)} candidates have a disclosed >{threshold}% shareholder "
        "(per i3investor's latest disclosure - verify manually).",
        file=sys.stderr,
    )
    print(f"Full shortlist (financials only) written to {out_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--max-marketcap", type=float, default=50.0, help="RM millions (default: 50)")
    parser.add_argument("--threshold", type=float, default=50.0, help="shareholder %% threshold (default: 50)")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between i3investor requests (default: 1)")
    parser.add_argument("--out", default="candidates.csv")
    args = parser.parse_args()
    run(max_marketcap=args.max_marketcap, threshold=args.threshold, delay=args.delay, out_path=args.out)


if __name__ == "__main__":
    main()
