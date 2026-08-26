"""Offline test for the klsescreener HTML row parser.

SAMPLE_HTML mirrors the actual response captured from klsescreener.com's
live quote_results endpoint via GitHub Actions CI (see
.github/workflows/run_screener.yml) - including the trailing "Indicators"
and action-icon cells that don't map to any Quote field, and the title
attributes the parser relies on.
"""
from bursa_screener.klse_screener import parse_quote_results

SAMPLE_HTML = """
<table><tbody>
<tr class="list">
<td title="GPP RESOURCES BERHAD"><a href="/v2/stocks/view/03029/gpp-resources-berhad">GPP</a>
<span style="font-size:8pt;color:#bbbbbb" title="Shariah Compliant">[s]</span>
</td>
<td title="Code">03029</td>
<td title="Category"><small>Industrial Services</small><br/><small class="text-muted"> Industrial Products &amp; Services, Leap Market</small></td>
<td title="Price 0.280-0.280" class="number ">0.280</td>
<td title="Change" class="number ">0</td>
<td title="Price 0.280-0.280" class="number ">0.0%</td>
<td title="52week" class="number">0.280-0.280</td>
<td title="Volume" class="number">0</td>
<td title="EPS" class="number">-5.38</td>
<td title="DPS" class="number">0.00</td>
<td title="NTA" class="number">-0.140</td>
<td title="PE" class="number">-5.21</td>
<td title="DY" class="number">0.00</td>
<td title="ROE" class="number">-38.43</td>
<td title="PTBV" class="number">-2.00</td>
<td title="Market Capital" class="number">45.20</td>
<td style="vertical-align: middle;line-height:1.5em;"></td>
<td title=""><a href="/v2/stocks/view/03029/gpp-resources-berhad"><i class="fa fa-info-circle"></i></a></td>
</tr>
</tbody></table>
"""


def test_parse_quote_results_basic_row():
    quotes = parse_quote_results(SAMPLE_HTML)
    assert len(quotes) == 1
    q = quotes[0]

    assert q.short_name == "GPP"
    assert q.name == "GPP RESOURCES BERHAD"
    assert q.code == "03029"
    assert q.category == "Industrial Services Industrial Products & Services"
    assert q.market == "Leap Market"
    assert q.price == 0.280
    assert q.changes_pct == 0.0
    assert q.week52_low == 0.280
    assert q.week52_high == 0.280
    assert q.volume == 0
    assert q.eps == -5.38
    assert q.dps == 0.00
    assert q.nta == -0.140
    assert q.pe == -5.21
    assert q.dy == 0.00
    assert q.roe == -38.43
    assert q.ptbv == -2.00
    assert q.market_cap_rm_mil == 45.20


def test_parse_quote_results_ignores_short_rows():
    html = "<table><tbody><tr class=\"list\"><td>only one cell</td></tr></tbody></table>"
    assert parse_quote_results(html) == []


def test_parse_quote_results_empty_when_no_matches():
    assert parse_quote_results("<html><body>no results</body></html>") == []
