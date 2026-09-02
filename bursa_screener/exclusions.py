"""Known syndicate / "corporate mafia" linked Bursa Malaysia counters to
exclude from acquisition screening.

This is a manually curated, sourced list - not something scraped or
inferred. It exists because a legitimate, well-documented case broke in
2025/2026: Bloomberg and The Edge Malaysia reported that businessman
Victor Chin Boon Long and associates (including Francis Leong See Wui)
allegedly used MACC investigations to pressure directors/shareholders of
several Bursa-listed companies into resigning or selling stakes at
undervalued prices, then took control via cross-shareholdings between the
companies themselves. Chin and associates reportedly held equity stakes in
close to 30 Bursa-listed companies in total; only the ones confirmed by
name in reporting are listed below - this is NOT a complete list of every
company the group has touched.

A stock landing on this list is a reason to investigate further by hand,
not necessarily proof the current board/major shareholder is complicit -
ownership and control can have changed since these reports. Always verify
current status before treating exclusion (or its absence) as final.

Sources:
- https://theedgemalaysia.com/node/793285 (Bloomberg expose on MACC/Azam Baki, Victor Chin)
- https://theedgemalaysia.com/node/796413 ("Corporate mafia exists but it's not me, says Victor Chin")
- https://theedgemalaysia.com/node/798075 (Cover Story: Who's who in the NexG saga)
- https://the-corporate-secret.com/blog/2023/08/20/... (Hong Seng / Classita acquisition)
"""
from __future__ import annotations

# code -> reason (with the syndicate-linked name(s) involved)
SYNDICATE_EXCLUSIONS: dict[str, str] = {
    "7154": (
        "NEXG BINA BERHAD (formerly Classita Holdings Bhd, formerly Caely "
        "Holdings Bhd) - named in the Victor Chin Boon Long 'corporate "
        "mafia' reporting; regulators have investigated cross-shareholding "
        "between Classita/NexG Bina, CSH Alliance (now Velocity Capital "
        "Partner), and Hong Seng Consolidated."
    ),
    "0200": (
        "REVENUE GROUP BERHAD - named by The Edge Malaysia as one of the "
        "companies Victor Chin Boon Long and associates held an equity "
        "stake in."
    ),
}


def is_excluded(code: str) -> bool:
    return code in SYNDICATE_EXCLUSIONS


def exclusion_reason(code: str) -> str:
    return SYNDICATE_EXCLUSIONS.get(code, "")
