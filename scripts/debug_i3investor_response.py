"""Diagnostic: dump what i3investor's substantial-shareholder page actually returns.

Not part of the package - a throwaway script to run in CI (which has real
internet access) to see why get_latest_substantial_shareholders() found no
shareholders for any of 141 real candidates.
"""
import sys

import requests

from bursa_screener.shareholder import source_url
from bursa_screener.utils import HEADERS

code = sys.argv[1] if len(sys.argv) > 1 else "03029"
url = source_url(code)
resp = requests.get(url, headers=HEADERS, timeout=30)
print("url:", url)
print("status:", resp.status_code)
print("len:", len(resp.text))
print("has <table:", "<table" in resp.text.lower())
print("num <th>:", resp.text.lower().count("<th"))
print("num <tr:", resp.text.lower().count("<tr"))
print("has captcha/cloudflare:", any(k in resp.text.lower() for k in ["captcha", "cloudflare", "checking your browser", "access denied", "login"]))
print("--- first 4000 chars ---")
print(resp.text[:4000])
