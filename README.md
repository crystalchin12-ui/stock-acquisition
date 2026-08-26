# stock-acquisition

Screens Bursa Malaysia listed companies for potential acquisition targets matching:

1. Net loss
2. Negative PE
3. Market cap < RM50 million
4. A single shareholder holding more than 50% of shares

## How it works

**Stage 1 - financials** (`bursa_screener/klse_screener.py`): queries
[klsescreener.com](https://www.klsescreener.com/v2/)'s screener backend
directly for negative PE + market cap < RM50m, then double-checks EPS < 0 as
well (net loss and negative PE are really the same signal, since price is
always positive - EPS < 0 is checked as a belt-and-suspenders confirmation).
This part is high confidence: the request format and HTML layout were taken
from a public reference implementation and the parser has an offline unit
test (`tests/test_klse_screener.py`).

**Stage 2 - majority shareholder** (`bursa_screener/shareholder.py`): for
each Stage 1 candidate, checks i3investor's substantial-shareholder
disclosure page for anyone holding >50%. **Read the caveats in that file's
docstring before trusting this output** - i3investor's page is a
transaction log of regulatory disclosures, not a live cap table, so this is
an estimate based on the most recently disclosed percentage per shareholder
name. Always confirm against the company's latest Annual Report ("Analysis
of Shareholdings") or a fresh Bursa LINK announcement before treating a
candidate as real.

## Important: run this somewhere with real internet access

This repository was authored inside a sandboxed Claude Code session whose
network egress proxy blocks klsescreener.com, i3investor.com, and
bursamalaysia.com outright. The klsescreener parsing logic was verified
offline against a synthetic HTML fixture; the i3investor logic could not be
exercised against live HTML at all. **Run this on your own machine** (or
any environment with normal internet access), and sanity-check the first
run's output by hand against the live sites.

## Usage

```bash
pip install -r requirements.txt
python -m bursa_screener.screen --out candidates.csv
```

Options:

- `--max-marketcap` - RM millions (default 50)
- `--threshold` - shareholder %% threshold (default 50)
- `--delay` - seconds between i3investor requests, be polite (default 1)
- `--out` - output CSV path

Output CSV columns: `code, name, market, price, eps, pe, market_cap_rm_mil,
top_shareholder, top_shareholder_pct, has_majority_shareholder,
verify_shareholding_url`.

Every row includes `verify_shareholding_url` so you can quickly manually
confirm any candidate i3investor scraping missed or got wrong.

## Tests

```bash
pip install -r requirements.txt
pytest tests/
```

Only the klsescreener parser is covered - it's the one piece that could be
tested without live network access. There's no test for the i3investor
module for the same reason.
