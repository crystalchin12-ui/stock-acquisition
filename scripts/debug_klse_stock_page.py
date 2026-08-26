"""Diagnostic: dump the full shareholding_changes table body from an
individual klsescreener stock page. Throwaway, run once in CI.
"""
import sys

import requests

from bursa_screener.utils import HEADERS

code = sys.argv[1] if len(sys.argv) > 1 else "2429"
url = f"https://www.klsescreener.com/v2/stocks/view/{code}"
resp = requests.get(url, headers=HEADERS, timeout=30)
html = resp.text
print("url:", url)
print("status:", resp.status_code, "len:", len(html))

start = html.find('id="shareholding_changes"')
if start == -1:
    print("shareholding_changes div not found")
else:
    # print a large chunk covering the whole table (thead + several tbody rows)
    print(html[start:start + 6000])
