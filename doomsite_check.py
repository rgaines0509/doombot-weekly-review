import aiohttp
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from language_tool_python import LanguageTool

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
    "https://quickbookstraining.com/privacy-policy",
    "https://quickbookstraining.com/learn-quickbooks"
]

tool = LanguageTool('en-US')


def format_grammar_results(matches):
    if not matches:
        return "✅ No grammar or spelling issues found."
    output = ["❌ Grammar/Spelling Issues Found:"]
    for match in matches:
        context = match.context.offset
        location = f"• Issue: {match.message}\n  Suggestion: {', '.join(match.replacements)}\n  Context: {match.context.text}\n"
        output.append(location)
    return "\n".join(output)


def format_tech_issues(broken_links, bad_toggles):
    lines = []
    if not broken_links:
        lines.append("✅ No broken links found.")
    else:
        lines.append("❌ Broken Links:")
        for link in broken_links:
            lines.append(f"• {link}")

    if not bad_toggles:
        lines.append("✅ No broken dropdowns found.")
    else:
        lines.append("❌ Broken Dropdowns:")
        for toggle in bad_toggles:
            lines.append(f"• {toggle}")

    return "\n".join(lines)


async def check_links_and_dropdowns(page):
    broken_links = []
    broken_toggles = []

    anchors = await page.query_selector_all("a")
    hrefs = [await a.get_attribute("href") for a in anchors if await a.get_attribute("href")]
    hrefs = [href for href in hrefs if href.startswith("http")]

    async with aiohttp.ClientSession() as session:
        for href in hrefs:
            try:
                async with session.get(href, timeout=10) as resp:
                    if resp.status >= 400:
                        broken_links.append(href)
            except Exception:
                broken_links.append(href)

    toggles = await page.query_selector_all(".dropdown-toggle, .accordion-toggle, .collapse-toggle")
    for toggle in toggles:
        try:
            await toggle.click()
            await asyncio.sleep(0.5)
            visible = await toggle.is_visible()
            if not visible:
                bad_toggles.append("Dropdown didn't expand properly")
        except Exception:
            bad_toggles.append("Error interacting with dropdown")

    return broken_links, bad_toggles


async def run_check(urls):
    report_sections = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        for url in urls:
            page = await context.new_page()
            try:
                await page.goto(url)
                await asyncio.sleep(2)
                html = await page.content()

                soup = BeautifulSoup(html, "html.parser")
                visible_text = soup.get_text()
                matches = tool.check(visible_text)

                broken_links, bad_toggles = await check_links_and_dropdowns(page)

                report_sections.append(f"=== {url} ===\n")
                report_sections.append("\n**Grammar Check:**\n")
                report_sections.append(format_grammar_results(matches))
                report_sections.append("\n**Technical Check:**\n")
                report_sections.append(format_tech_issues(broken_links, bad_toggles))
                report_sections.append("\n")

            except Exception as e:
                report_sections.append(f"❌ Failed to check {url}: {e}\n")

        await browser.close()

    return report_sections











