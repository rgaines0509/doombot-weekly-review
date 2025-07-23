"""
Doombot Site Checker – Fast version
- No Playwright, no LanguageTool
- Checks ONLY the first 10 links per page
- Scans all URLs concurrently for max speed
"""

import asyncio
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

# ─────────────── CONFIG ──────────────────────────────────────────────────────
PAGE_TIMEOUT      = 15      # seconds for the main page fetch
LINK_TIMEOUT      = 5       # seconds for each link HEAD/GET
MAX_LINKS_PER_PAGE = 10     # <── Option 1: cap link checks here
DROPDOWN_KEYWORDS = ("dropdown", "accordion", "collapse")
HEADERS           = {"User-Agent": "DoombotSiteChecker/1.0"}
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────── HELPERS ─────────────────────────────────────────────────────
def _abs_url(base: str, link: str) -> str:
    """Resolve relative link to absolute URL."""
    return urllib.parse.urljoin(base, link)


def _fetch(url: str, timeout: int) -> requests.Response:
    """Blocking HTTP GET wrapped later in asyncio.to_thread."""
    return requests.get(url, timeout=timeout, headers=HEADERS, allow_redirects=True)


def _find_dropdowns(soup: BeautifulSoup) -> List[str]:
    """Return snippets of elements that look like dropdowns/accordions."""
    dropdowns = []

    dropdowns += [str(tag)[:80] + "…" for tag in soup.find_all("summary")]

    dropdowns += [
        str(tag)[:80] + "…"
        for tag in soup.find_all("button", attrs={"aria-expanded": True})
    ]

    dropdowns += [
        str(tag)[:80] + "…"
        for kw in DROPDOWN_KEYWORDS
        for tag in soup.select(f'.{kw}')
    ]

    return dropdowns
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────── PER-PAGE CHECK ──────────────────────────────────────────────
async def check_single_url(url: str) -> Dict[str, Any]:
    print(f"🔍 Fetching {url}")
    try:
        resp = await asyncio.to_thread(_fetch, url, PAGE_TIMEOUT)
        html = resp.text
        status = resp.status_code
    except Exception as e:
        return {"url": url, "error": str(e), "checked_at": datetime.utcnow().isoformat()}

    if status != 200:
        return {"url": url, "error": f"HTTP {status}", "checked_at": datetime.utcnow().isoformat()}

    soup = BeautifulSoup(html, "lxml")

    # -- Broken-link scan (first 10 links only) -------------------------------
    links = [a.get("href") for a in soup.find_all("a", href=True)][:MAX_LINKS_PER_PAGE]
    broken_links = []

    async def check_l_









