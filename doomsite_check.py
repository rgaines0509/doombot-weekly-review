import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import aiohttp

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

LANGUAGETOOL_ENDPOINT = "https://api.languagetool.org/v2/check"

async def check_grammar(text, session):
    if not text or len(text.strip()) < 10:
        return ["⚠️ No readable text to analyze."]
    try:
        payload = {
            "text": text[:5000],  # Cap for API safety
            "language": "en-US"
        }
        async with session.post(LANGUAGETOOL_ENDPOINT, data=payload) as resp:
            if resp.status != 200:
                return [f"❌ LanguageTool API error: {resp.status}"]
            data = await resp.json()
            return [
                f"{match['rule']['issueType'].upper()}: {match['message']} (Context: '{match['context']['text']}')"
                for match in data.get("matches", [])
            ]
    except Exception as e:
        return [f"❌ Grammar check failed: {str(e)}"]

async def analyze_page(url, session, playwright):
    result = {"url": url, "broken_links": [], "dropdowns": [], "grammar_errors": []}

    try:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        response = await page.goto(url)

        if not response or not response.ok:
            result["error"] = f"Page load failed (status: {response.status if response else 'N/A'})"
            await browser.close()
            return result

        # Extract page content
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        # Check dropdowns
        dropdowns = soup.find_all("details")
        for d in dropdowns:
            try:
                handle = await page.query_selector("details")
                if handle:
                    visible = await handle.is_visible()
                    result["dropdowns"].append("Pass" if visible else "Fail")
            except:
                result["dropdowns"].append("Fail")

        # Check all links
        links = [a.get("href") for a in soup.find_all("a", href=True) if a.get("href").startswith("http")]
        for link in links:
            try:
                async with session.get(link, timeout=10) as resp:
                    if resp.status >= 400:
                        result["broken_links"].append((link, resp.status))
            except:
                result["broken_links"].append((link, "Request failed"))

        # Grammar/spelling check
        page_text = soup.get_text(separator=' ', strip=True)
        result["grammar_errors"] = await check_grammar(page_text, session)

        await browser.close()

    except Exception as e:
        result["error"] = str(e)

    return result

async def run_check(urls):
    async with async_playwright() as playwright:
        async with aiohttp.ClientSession() as session:
            tasks = [analyze_page(url, session, playwright) for url in urls]
            results = await asyncio.gather(*tasks)
    return results









