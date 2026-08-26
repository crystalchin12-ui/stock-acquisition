"""Diagnostic: can a real (headless) browser get past i3investor's Cloudflare
challenge where a plain HTTP request (see the removed debug_i3investor_response.py,
captured in git history) got a straight 403?

Not part of the package - a throwaway script run once in CI to answer that
question. If it works, the plan is to swap this fetch strategy into
shareholder.py; if not, Stage 2 stays as manual-review-only.
"""
import sys

from playwright.sync_api import sync_playwright

from bursa_screener.shareholder import source_url

code = sys.argv[1] if len(sys.argv) > 1 else "03029"
url = source_url(code)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    )
    page.goto(url, timeout=30000)
    # Cloudflare's managed challenge can take a few seconds to resolve itself
    # in a real browser context; give it room before deciding.
    page.wait_for_timeout(8000)

    title = page.title()
    html = page.content()
    print("url:", url)
    print("title:", title)
    print("still on challenge page:", "just a moment" in title.lower())
    print("has <table:", "<table" in html.lower())
    print("num <th>:", html.lower().count("<th"))
    print("html length:", len(html))
    print("--- first 3000 chars of rendered HTML ---")
    print(html[:3000])

    browser.close()
