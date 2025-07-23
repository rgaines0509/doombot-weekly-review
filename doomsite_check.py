import asyncio
import re
from playwright.async_api import async_playwright
import aiohttp

APPROVED_URLS = [
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
    "https://quickbookstraining.com/privacy-policy",
]

MAX_TEXT_FOR_GRAMMAR = 5000

async def check_dropdowns(page):
    dropdowns = await page.query_selector_all("details, summary, .dropdown, .accordion, .faq-toggle, [aria-expanded]")
    results = []

    for idx, dropdown in enumerate(dropdowns):
        try:
            await dropdown.click()
            await page.wait_for_timeout(500)
            visible = await dropdown.is_visible()
            results.append("Pass" if visible else "Fail")
        except:
            results.append("Fail")

    return results

async def check_links(page):
    links = await page.query_selector_all("a[href]")
    broken_links = []
    async with aiohttp.ClientSession() as session:
        for link in links:
            href = await link.get_attribute("href")
            if not href or not href.startswith("http"):
                continue
            try:
                async with session.get(href, timeout=10) as response:
                    if response.status >= 400:
                        broken_links.append((href, response.status))
            except Exception as e:
                broken_links.append((href, "timeout or error"))

    return broken_links

async def check_grammar(text):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://api.languagetool.org/v2/check",
                data={
                    "text": text[:MAX_TEXT_FOR_GRAMMAR],
                    "language": "en-US"
                },
                timeout=15
            ) as resp:
                data = await resp.json()
                return [
                    f"{match['message']} (at position {match['offset']} in: '{match['context']['text']}')"
                    for match in data.get("matches", [])
                ]
        except Exception as e:
            return [f"Grammar check failed: {str(e)}"]

async def analyze_page(playwright, url):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    result = {"url": url}

    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("load")

        result["dropdowns"] = await check_dropdowns(page)
        result["broken_links"] = await check_links(page)
        content = await page.content()
        text = re.sub('<[^<]+?>', '', content)
        result["grammar_errors"] = await check_grammar(text)

    except Exception as e:
        result["error"] = str(e)

    await browser.close()
    return result

async def run_check(urls):
    async with async_playwright() as p:
        tasks = [analyze_page(p, url) for url in urls]
        return await asyncio.gather(*tasks)

# Expose this for main.py
__all__ = ["run_check"]









