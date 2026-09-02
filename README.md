# stock-acquisition

Screens Bursa Malaysia listed companies for potential acquisition targets matching:

1. Net loss
2. Negative PE
3. Market cap < RM50 million
4. A single shareholder holding more than 50% of shares
5. Not a known syndicate/"corporate mafia"-linked counter (excluded by default)

## Status (confirmed against the live sites via GitHub Actions CI)

**Stage 1 - financials: works.** Queries
[klsescreener.com](https://www.klsescreener.com/v2/)'s screener backend
(`bursa_screener/klse_screener.py`) for negative PE + market cap < RM50m,
then confirms EPS < 0 as well. As of the last live CI run this correctly
found **141 real counters** matching all three financial criteria. The
site's HTML layout doesn't quite match older third-party documentation of
it (it has an extra "Change" column that shifts naive positional parsing),
so the parser locates fields by each cell's `title` attribute instead of
raw position - see the module docstring for the full story, and
`tests/test_klse_screener.py` for an offline regression test built from
real captured HTML.

**Stage 2 - majority shareholder: does not work, by design falls back to
manual review.** `bursa_screener/shareholder.py` was written to check
i3investor's substantial-shareholder disclosure page per candidate, but
i3investor.com sits behind a Cloudflare "managed challenge" - every
request gets HTTP 403 and a JavaScript challenge page instead of real
data. That's confirmed live, not a guess, and it's not something a plain
HTTP request can get past. **`python -m bursa_screener.screen` does not
attempt this check by default** (see `--attempt-shareholder-check` if you
want to try anyway, e.g. after swapping in a browser-based fetcher that
can pass the challenge). Every output row instead carries a
`verify_shareholding_url` - check that by hand, or against the company's
latest Annual Report ("Analysis of Shareholdings" section), before
treating any candidate as a real target. Even if the Cloudflare gate were
solved, i3investor's page is a disclosure transaction log rather than a
clean live cap table, so it would still only be an estimate - see
`shareholder.py`'s module docstring for the full detail.

**Exclusion list - syndicate/"corporate mafia"-linked counters.**
`bursa_screener/exclusions.py` maintains a manually curated, sourced list
of Bursa-listed counters publicly reported (Bloomberg, The Edge Malaysia)
as linked to the Victor Chin Boon Long "corporate mafia" case - businessmen
alleged to have used MACC investigations to pressure shareholders into
selling stakes at undervalued prices, then taken control via
cross-shareholdings. `python -m bursa_screener.screen` excludes any such
counter from its output by default; pass `--include-flagged` to keep them
in (e.g. to review why they were flagged). This is **not** a complete list
of every company the group has touched (reporting says Chin and associates
held stakes in close to 30 counters) - only the ones confirmed by name in
reporting are listed, so treat exclusion (or its absence) as a starting
point for manual due diligence, not a final verdict.

## Usage

```bash
pip install -r requirements.txt
python -m bursa_screener.screen --out candidates.csv
```

Options:

- `--max-marketcap` - RM millions (default 50)
- `--threshold` - shareholder %% threshold, only relevant with `--attempt-shareholder-check` (default 50)
- `--attempt-shareholder-check` - try the i3investor check anyway (currently always fails, see Status above)
- `--delay` - seconds between i3investor requests when attempting the check (default 1)
- `--out` - output CSV path

Output CSV columns: `code, name, market, price, eps, pe, market_cap_rm_mil,
top_shareholder, top_shareholder_pct, has_majority_shareholder,
verify_shareholding_url`. The last four columns are blank/unpopulated
unless you pass `--attempt-shareholder-check` - `verify_shareholding_url`
is always populated so you can check by hand.

A GitHub Actions workflow (`.github/workflows/run_screener.yml`) runs this
on every push to this branch (and via manual dispatch) - useful since this
project was authored in a sandboxed session with no route to
klsescreener.com or i3investor.com; CI is how Stage 1 was actually
verified against live data.

## Tests

```bash
pip install -r requirements.txt
pytest tests/
```

Only the klsescreener parser is covered by an offline test - it's the
piece that was fixable and verifiable without live network access. There's
no test for the i3investor module since it doesn't currently work.
