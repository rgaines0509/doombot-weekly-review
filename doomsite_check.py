import asyncio
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
import language_tool_python

# ---------- CONFIG ----------------------------------------------------------
PAGE_TIMEOUT      = 15   # seconds for the initial page fetch
LINK_TIMEOUT      = 5    # seconds per internal/external link check
MAX_TEXT_LENGTH   = 20_000
GRAMMAR_TIMEOUT   = 20   # seconds per grammar run
DROPDOWN_KEYWORDS = ("dropdown", "accordion", "collapse")  # class name hints
# ---------------------------------------------------------------------------

tool = language_tool_python.LanguageTool('en-US')


# ---------- CORE HELPERS ----------------------------------------------------
def _abs_url(base: str, link: str) -> str:
    """Resolve relative link to absolute."""
    return urllib.parse.urljoin(base, link)


def _fetch(url: str, timeout: int) -> requests.Response:
    """Thin wrapper around requests.get with a timeout."""
    return requests.get(url, timeout=timeout, headers={"User-Agent": "DoombotSiteChecker/1.0"})


def _find_dropdowns(soup: BeautifulSoup) -> List[str]:
    """Return simple descriptors for elements that *look* like dropdowns/accordions."""
    dropdowns = []

    # <summary> (HTML5 details/summary accordion)
    dropdowns += [str(tag)[:80] + "…" for tag in soup.find_all("summary")]

    # <button aria-expanded="false|true">
    dropdowns += [
        str(tag)[:80] + "…"
        for tag in soup.find_all("button", attrs={"aria-expanded": True})
    ]

    # Any element whose class contains dropdown/accordion/collapse
    dropdowns += [
        str(tag)[:80] + "…"
        for kw in DROPDOWN_KEYWORDS
        for tag in soup.select(f'.{kw}')
    ]

    return dropdowns
# ---------------------------------------------------------------------------


# ---------- PAGE-LEVEL CHECK ------------------------------------------------
async def check_single_url(url: str) -> Dict[str, Any]:
    """Fetch a page, test links, detect dropdown-like elements, grammar-scan visible text."""
    print(f"⏳ Fetching {url}")
    try:
        resp: requests.Response = await asyncio.to_thread(_fetch, url, PAGE_TIMEOUT)
        status = resp.status_code
        if status != 200:
            return {"url": url, "error": f"HTTP {status}"}
        html = resp.text
    except Exception as e:
        return {"url": url, "error": str(e)}

    soup = BeautifulSoup(html, "lxml")

    # ---- broken-link scan ---------------------------------------------------
    links = [a.get("href") for a in soup.find_all("a", href=True)]
    broken_links = []
    for link in links:
        abs_link = _abs_url(url, link)
        try:
            r = await asyncio.to_thread(_fetch, abs_link, LINK_TIMEOUT)
            if r.status_code != 200:
                broken_links.append((abs_link, r.status_code))
        except Exception as e:
            broken_links.append((abs_link, str(e)))

    # ---- dropdown detection -------------------------------------------------
    dropdown_candidates = _find_dropdowns(soup)

    # ---- grammar & spelling -------------------------------------------------
    visible_text = " ".join(
        el.get_text(" ", strip=True)
        for el in soup.find_all(
            ["p", "li", "span", "div", "h1", "h2", "h3", "h4", "h5", "h6"]
        )
    ).strip()

    grammar_errors = []
    if visible_text and len(visible_text) < MAX_TEXT_LENGTH:
        try:
            matches = await asyncio.wait_for(
                asyncio.to_thread(tool.check, visible_text),
                timeout=GRAMMAR_TIMEOUT,
            )
            for m in matches:
                ctx = m.context[:75].replace("\n", " ")
                grammar_errors.append(
                    f"✏️ {m.message} | Suggest: {m.replacements} | “…{ctx}…”"
                )
        except asyncio.TimeoutError:
            grammar_errors.append("⚠️ Grammar check timed out.")
        except Exception as e:
            grammar_errors.append(f"⚠️ Grammar check failed: {e}")
    elif not visible_text:
        grammar_errors.append("ℹ️ No visible text found.")
    else:
        grammar_errors.append("ℹ️ Text too long, grammar skipped.")

    return {
        "url": url,
        "checked_at": datetime.utcnow().isoformat(),
        "broken_links": broken_links,
        "dropdowns": dropdown_candidates,
        "grammar_errors": grammar_errors,
    }
# ---------------------------------------------------------------------------


# ---------- PUBLIC ENTRYPOINT ----------------------------------------------
async def run_check(urls: List[str]) -> List[Dict[str, Any]]:
    """Main entry called by `main.py`.  Returns list of per-URL result dicts."""
    results = []
    for u in urls:
        res = await check_single_url(u)
        results.append(res)
    return results
# ---------------------------------------------------------------------------







