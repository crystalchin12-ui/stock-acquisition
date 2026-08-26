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

positions = [m.start() for m in re.finditer(r"shareholding", html, re.I)]
print("'shareholding' occurrences:", len(positions), positions)

for pos in positions:
    print(f"--- context around offset {pos} ---")
    print(html[max(0, pos - 200):pos + 800])
    print()
