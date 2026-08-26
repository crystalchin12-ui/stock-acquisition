"""Offline test for the klsescreener HTML row parser.

Exercises parse_quote_results() against a synthetic row built to match the
tbody/tr.list/td-index layout documented in klse_screener.py's module
docstring, since the live site is not reachable from this test environment.
"""
from bursa_screener.klse_screener import parse_quote_results

SAMPLE_HTML = """
<table><tbody>
<tr class="list">
<td title="ABC BERHAD">[s]ABCB</td>
<td>1234</td>
<td>Main Market,Technology</td>
<td>0.150</td>
<td>-2.5%</td>
<td>0.100 - 0.250</td>
<td>1,234,500</td>
<td>-0.05</td>
<td>0.00</td>
<td>0.080</td>
<td>-3.00</td>
<td>0.00</td>
<td>-10.50</td>
<td>1.88</td>
<td>45.20</td>
</tr>
</tbody></table>
"""


def test_parse_quote_results_basic_row():
    quotes = parse_quote_results(SAMPLE_HTML)
    assert len(quotes) == 1
    q = quotes[0]

    assert q.short_name == "ABCB"
    assert q.name == "ABC BERHAD"
    assert q.code == "1234"
    assert q.category == "Main Market"
    assert q.market == "Technology"
    assert q.price == 0.150
    assert q.changes_pct == -2.5
    assert q.week52_low == 0.100
    assert q.week52_high == 0.250
    assert q.volume == 1234500
    assert q.eps == -0.05
    assert q.dps == 0.00
    assert q.nta == 0.080
    assert q.pe == -3.00
    assert q.dy == 0.00
    assert q.roe == -10.50
    assert q.ptbv == 1.88
    assert q.market_cap_rm_mil == 45.20


def test_parse_quote_results_ignores_short_rows():
    html = "<table><tbody><tr class=\"list\"><td>only one cell</td></tr></tbody></table>"
    assert parse_quote_results(html) == []


def test_parse_quote_results_empty_when_no_matches():
    assert parse_quote_results("<html><body>no results</body></html>") == []
