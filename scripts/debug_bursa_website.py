"""Diagnostic: is bursamalaysia.com itself reachable (unlike i3investor), and
does it expose substantial-shareholder / announcement data per stock?
Throwaway, run once in CI.
"""
import requests

from bursa_screener.utils import HEADERS

urls = [
    "https://www.bursamalaysia.com/market_information/announcements/company_announcement",
    "https://www.bursamalaysia.com/market_information/equities_prices",
]

for url in urls:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        print("url:", url)
        print("status:", resp.status_code, "len:", len(resp.text))
        print("has captcha/cloudflare/akamai:", any(k in resp.text.lower() for k in ["captcha", "just a moment", "access denied", "akamai"]))
        print()
    except requests.RequestException as e:
        print("url:", url)
        print("FAILED:", type(e).__name__, str(e)[:200])
        print()
