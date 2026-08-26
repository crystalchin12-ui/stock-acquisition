"""Diagnostic: does klsescreener.com's /v2/shareholdings page carry the
substantial-shareholder data we need, and is it reachable (unlike
i3investor, which is Cloudflare-blocked)? Throwaway, run once in CI.
"""
import requests

from bursa_screener.utils import HEADERS

url = "https://www.klsescreener.com/v2/shareholdings"
resp = requests.get(url, headers=HEADERS, timeout=30)
print("url:", url)
print("status:", resp.status_code)
print("len:", len(resp.text))
print("has <table:", "<table" in resp.text.lower())
print("has captcha/cloudflare:", any(k in resp.text.lower() for k in ["captcha", "cloudflare", "just a moment"]))
print("--- first 5000 chars ---")
print(resp.text[:5000])
