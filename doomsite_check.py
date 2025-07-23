import asyncio
import aiohttp
from bs4 import BeautifulSoup
from language_tool_python import LanguageTool
from playwright.async_api import async_playwright

URLS_TO_CHECK = [
    "https://quickbookstraining.com/",
    "https://quickbookstraining.com/live-quickbooks-help",
    "https://quickbookstraining.com/quickbooks-courses",
    "https://quickbookstraining.com/quickbooks-classes",
    "https://quickbookstraining.com/plans-and-pricing",
    "https://quickbookstraining.com/about-us",
    "https://quickbookstraining.com/contact-us",
    "https://quickbookstraining.com/quickbooks-certification",
    "https://quickbookstraining.com/quickbooks-online-certification",
    "https://quickbookstraining.com/quickbooks-desktop-certification",
    "https://quickbookstraining.com/quickbooks-bookkeeping-certification",
    "https://quickbookstraining.com/quickbooks-certification-online",
    "https://quickbookstraining.com/quickbooks-certification-exam",
    "https://quickbookstraining.com/terms-and-conditions",
    "https://quickbookstraining.com/privacy-policy"
]

# Use the public API instead of trying to start a server
tool = LanguageTool('en-US', remote_server='https://api.languagetool.org/v2/')

async def check_links(session, url):
    broken_links = []
    try:
        async with session.get(url, timeout=15) as response:
            if response.status != 200:
                return [(url, response.status)]
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if href.startswith("http"):
                    try:
                        async with session.get(href, timeout=10) as link_response:
                            if link_response.status >= 400:
                                broken_links.append((href, link_response.status))
                    except Exception:
                        broken_links.append((href, "timeout/fail"))
            return broken_links
    except Exception:
        return [(url, "page-load-failure")]

async def check_dropdowns(page):
    dropdowns = []
    elements = await page.query_selector_all('[aria-expanded], .dropdown, nav ul li')
    for el in elements:
        try:
            visible = await el.is_visible()
            if not visible:
                dropdowns.append("Fail")
            else:
                dropdowns.append("Pass")
        except Exception:
            dropdowns.append("Fail")
    return dropdowns

async def analyze_page(playwright, session, url):
    print(f"🔍 Checking {url}")
    result = {"url": url, "broken_links": [], "dropdowns": [], "grammar_errors": []}

    try:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        dropdown_results = await check_dropdowns(page)
        result["dropdowns"] = dropdown_results
        html = await page.content()
        await browser.close()
    except Exception as e:
        result["error"] = f"Failed to load with Playwright: {str(e)}"
        return result

    soup = BeautifulSoup(html, 'html.parser')

    # Link Check
    result["broken_links"] = await check_links(session, url)

    # Grammar Check (Safe mode)
    try:
        text = soup.get_text(separator=' ', strip=True)
        if text and len(text.strip()) > 10:
            matches = tool.check(text[:5000])
            grammar_errors = [f"{m.ruleIssueType.upper()}: {m.message} (Context: '{m.context.text}')" for m in matches]
            result["grammar_errors"] = grammar_errors
        else:
            result["grammar_errors"] = ["⚠️ No readable text to analyze."]
    except Exception as e:
        result["grammar_errors"] = [f"⚠️ Grammar check failed: {str(e)}"]

    return result

async def run_check(urls):
    async with aiohttp.ClientSession() as session:
        async with async_playwright() as p:
            tasks = [analyze_page(p, session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results










