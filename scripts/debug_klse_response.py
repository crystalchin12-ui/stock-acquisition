"""Diagnostic: dump what klsescreener.com's screener endpoint actually returns.

Not part of the package - a throwaway script to run in CI (which has real
internet access) to see why fetch_quotes() found 0 rows.
"""
import requests

from bursa_screener.klse_screener import QUOTE_RESULTS_URL, REQUEST_HEADERS

payload = {"getquote": "1", "max_pe": "-0.01", "max_marketcap": "50"}
resp = requests.post(QUOTE_RESULTS_URL, data=payload, headers=REQUEST_HEADERS, timeout=30)
print("status:", resp.status_code)
print("len:", len(resp.text))
print("has tr.list marker:", 'tr class="list"' in resp.text or "tr class='list'" in resp.text)
print("has <table:", "<table" in resp.text.lower())
print("has captcha/cloudflare:", any(k in resp.text.lower() for k in ["captcha", "cloudflare", "checking your browser", "access denied"]))
print("--- first 3000 chars ---")
print(resp.text[:3000])
print("--- last 1000 chars ---")
print(resp.text[-1000:])
