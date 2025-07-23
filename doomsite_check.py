import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests

MAX_LINK_TIMEOUT = 5

async def check_page(page, url):
    print(f"\n⏳ Navigating to {url} ...")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    except Exception as e:
        print(f"❌ Page load failed or timed out for {url}: {e}")
        return {
            "url": url,
            "error": f"Page load failed: {e}",
            "broken_links": [],
            "dropdowns": [],
            "grammar_errors": ["⚠️ Page failed to load — grammar check skipped."]
        }

    # Collect all links
    links = await page.eval_on_selector_all("a[href]", "elements => elements.map(el => el.href)")
    broken_links = []

    for link in links:
        try:
            res = requests.get(link, timeout=MAX_LINK_TIMEOUT)
            if res.status_code != 200:
                broken_links.append((link, res.status_code))
        except Exception as e:
            broken_links.append((link, str(e)))

    # Check dropdowns/toggles
    dropdowns = await page.query_selector_all("summary, button, .dropdown, .accordion")
    dropdown_results = []
    for d in dropdowns:
        try:
            await d.click()
            await page.wait_for_timeout(300)
            dropdown_results.append("Success")
        except Exception:
            dropdown_results.append("Fail")

    # Skip grammar entirely for performance testing
    grammar_errors = ["⚠️ Grammar check disabled for performance test."]

    return {
        "url": url,
        "broken_links": broken_links,
        "dropdowns": dropdown_results,
        "grammar_errors": grammar_errors
    }

async def run_check(urls):
    report = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for url in urls:
            try:
                result = await check_page(page, url)
                report.append(result)
            except Exception as e:
                report.append({"url": url, "error": str(e)})
                print(f"❌ Error checking {url}: {e}")

        await browser.close()

    return report




