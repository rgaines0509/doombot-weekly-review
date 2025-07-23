import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from language_tool_python import LanguageTool
from playwright.async_api import async_playwright

tool = LanguageTool('en-US')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Doombot/1.0; +https://quickbookstraining.com)"
}

async def fetch_page(url, session):
    try:
        async with session.get(url, headers=HEADERS) as response:
            html = await response.text()
            return html, response.status
    except Exception as e:
        return None, str(e)

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http") or href.startswith("/"):
            full_url = href if href.startswith("http") else base_url.rstrip("/") + href
            links.append(full_url)
    return links

def extract_text_with_context(html):
    soup = BeautifulSoup(html, "html.parser")
    text_blocks = []

    for tag in soup.find_all(string=True):
        text = tag.strip()
        if text and len(text.split()) > 2:
            path = " > ".join(
                [parent.name for parent in tag.parents if parent.name not in ["html", "body"]][::-1]
            )
            text_blocks.append((path, text))
    return text_blocks

async def check_link(url, session):
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as response:
            return url, response.status
    except Exception:
        return url, "error"

async def check_dropdowns(url, page):
    dropdown_results = []
    try:
        await page.goto(url, timeout=60000)
        dropdowns = await page.query_selector_all("button, summary")
        for dropdown in dropdowns:
            try:
                visible = await dropdown.is_visible()
                if not visible:
                    dropdown_results.append("Fail")
                    continue
                await dropdown.click()
                dropdown_results.append("Pass")
            except Exception:
                dropdown_results.append("Fail")
    except Exception:
        dropdown_results.append("Fail")
    return dropdown_results

async def analyze_page(url, session, browser):
    result = {"url": url}
    html, status = await fetch_page(url, session)

    if html is None:
        result["error"] = f"Unable to load: {status}"
        return result

    result["broken_links"] = []
    result["dropdowns"] = []
    result["grammar_errors"] = []

    # Check links
    links = extract_links(html, url)
    link_tasks = [check_link(link, session) for link in links]
    link_results = await asyncio.gather(*link_tasks)

    for link, code in link_results:
        if isinstance(code, int) and (code >= 400 or code == 0):
            result["broken_links"].append((link, code))
        elif code == "error":
            result["broken_links"].append((link, code))

    # Check dropdowns
    page = await browser.new_page()
    dropdowns = await check_dropdowns(url, page)
    await page.close()
    result["dropdowns"] = dropdowns

    # Grammar/spelling
    text_blocks = extract_text_with_context(html)
    grammar_issues = []
    for path, text in text_blocks:
        matches = tool.check(text)
        for match in matches:
            snippet = f"{path}: {text[match.offset:match.offset + match.errorLength]}"
            grammar_issues.append(snippet)
    result["grammar_errors"] = grammar_issues

    return result

async def run_check(urls):
    async with aiohttp.ClientSession() as session:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            tasks = [analyze_page(url, session, browser) for url in urls]
            results = await asyncio.gather(*tasks)
            await browser.close()
    return results










