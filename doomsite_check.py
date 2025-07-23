import asyncio
from playwright.async_api import async_playwright

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

    # Check dropdowns/toggles only
    dropdowns = await page.query_selector_all("summary, button, .dropdown, .accordion")
    dropdown_results = []
    for d in dropdowns:
        try:
            await d.click()
            await page.wait_for_timeout(300)
            dropdown_results.append("Success")
        except Exception:
            dropdown_results.append("Fail")

    return {
        "url": url,
        "broken_links": ["⚠️ Link checking disabled in test mode."],
        "dropdowns": dropdown_results,
        "grammar_errors": ["⚠️ Grammar check disabled in test mode."]
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





