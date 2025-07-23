import asyncio
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

PAGE_TIMEOUT      = 15
LINK_TIMEOUT      = 5
DROPDOWN_KEYWORDS = ("dropdown", "accordion", "collapse")

def _abs_url(base: str, link: str) -> str:
    return urllib.parse.urljoin(base, link)

def _fetch(url: str, timeout: int) -> requests.Response:
    return requests.get(url, timeout=timeout, headers={"User-Agent": "DoombotSiteChecker/1.0"})

def _find_dropdowns(soup: BeautifulSoup) -> List[str]:
    dropdowns = []
    dropdowns += [str(tag)[:80] + "…" for tag in soup.find_all("summary")]
    dropdowns += [str(tag)[:80] + "…" for tag in soup.find_all("button", attrs={"aria-expanded": True})]
    dropdowns += [str(tag)[:80] + "…" for kw in DROPDOWN_KEYWORDS for tag in soup.select(f'.{kw}')]
    return dropdowns

async def check_single_url(url: str) -> Dict[str, Any]:
    print(f"⏳ Fetching {url}")
    try:
        resp = await asyncio.to_thread(_fetch, url, PAGE_TIMEOUT)
        html = resp.text
    except Exception as e:
        return {"url": url, "error": str(e)}

    soup = BeautifulSoup(html, "lxml")

    links = [a.get("href") for a in soup.find_all("a", href=True)]
    broken_links = []
    for link in links[:20]:
        abs_link = _abs_url(url, link)
        try:
            r = await asyncio.to_thread(_fetch, abs_link, LINK_TIMEOUT)
            if r.status_code != 200:
                broken_links.append((abs_link, r.status_code))
        except Exception as e:
            broken_links.append((abs_link, str(e)))

    dropdowns = _find_dropdowns(soup)

    return {
        "url": url,
        "checked_at": datetime.utcnow().isoformat(),
        "broken_links": broken_links,
        "dropdowns": dropdowns,
        "grammar_errors": ["⚠️ Grammar check disabled (to fix LanguageTool hang)."]
    }

async def run_check(urls: List[str]) -> List[Dict[str, Any]]:
    results = []
    for u in urls:
        res = await check_single_url(u)
        results.append(res)
    return results








