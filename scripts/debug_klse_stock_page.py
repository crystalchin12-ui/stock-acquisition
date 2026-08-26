"""Diagnostic: does an individual klsescreener stock page carry current
substantial-shareholder / major-shareholder data (not just the global
recent-changes feed)? Throwaway, run once in CI.
"""
import re
import sys

import requests

from bursa_screener.utils import HEADERS

code = sys.argv[1] if len(sys.argv) > 1 else "03029"
url = f"https://www.klsescreener.com/v2/stocks/view/{code}"
resp = requests.get(url, headers=HEADERS, timeout=30)
html = resp.text
print("url:", url)
print("status:", resp.status_code, "len:", len(html))

for kw in ["shareholding", "Major Shareholder", "Substantial Shareholder", "shareholder"]:
    idxs = [m.start() for m in re.finditer(re.escape(kw), html, re.I)]
    print(f"'{kw}' occurrences: {len(idxs)}", idxs[:5])

# print context around first "shareholding"-ish match
m = re.search(r"shareholding|shareholder", html, re.I)
if m:
    print("--- context around first match ---")
    print(html[max(0, m.start() - 300):m.start() + 3000])
else:
    print("no match found")
