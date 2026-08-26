"""Diagnostic: inspect klsescreener.com's /v2/shareholdings page structure -
is it per-stock searchable, and does it have current % ownership data?
Throwaway, run once in CI.
"""
import re

import requests

from bursa_screener.utils import HEADERS

url = "https://www.klsescreener.com/v2/shareholdings"
resp = requests.get(url, headers=HEADERS, timeout=30)
html = resp.text
print("status:", resp.status_code, "len:", len(html))

# find the table area
idx = html.lower().find("<table")
print("--- table area (2000 chars from first <table) ---")
print(html[idx:idx + 2000])

print("--- table headers (<th> tags) ---")
for m in re.finditer(r"<th[^>]*>(.*?)</th>", html, re.S | re.I):
    print(repr(re.sub(r"\s+", " ", m.group(1)).strip()))

print("--- form inputs / selects (possible search-by-stock) ---")
for m in re.finditer(r"<(input|select)[^>]*>", html, re.I):
    print(m.group(0)[:200])

print("--- any ajax/api endpoint hints in inline scripts mentioning 'shareholding' ---")
for m in re.finditer(r"[\"']([^\"']*shareholding[^\"']*)[\"']", html, re.I):
    print(m.group(1))
