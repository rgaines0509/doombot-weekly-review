import aiohttp
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from language_tool_python import LanguageTool
import re

tool = LanguageTool('en-US', remote_server='https://api.languagetoolplus.com/v2/')
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

async def fetch_html(url, session):
    try:
        async with session.get(url, timeout=10) as response:
            return await response.text()
    except Exception as e:
        return f"<html><body><p>Error fetching {url}: {str(e)}</p></body></html>"

async def check_links_and_dropdowns(page, url):
    report = []
    await page.goto(url, wait_until='domcontentloaded')
    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')

    anchors = soup.find_all('a', href=True)
    dropdowns = soup.select('.dropdown-toggle, .menu-toggle, .toggle')

    for anchor in anchors:
        link = anchor['href']
        if not link.startswith('http'):
            continue
        try:
            response = await page.context.new_page()
            await response.goto(link, timeout=10000)
            await response.close()
        except Exception:
            report.append(f"❌ Broken link: {link}")

    for toggle in dropdowns:
        try:
            selector = toggle.get('class')[0]
            await page.click(f'.{selector}')
        except Exception:
            report.append(f"⚠️ Dropdown/toggle failed: {toggle}")

    return report

async def analyze_page(url, session, page):
    html = await fetch_html(url, session)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')
    matches = tool.check(text)

    grammar_issues = []
    for match in matches:
        snippet = text[match.offset:match.offset + match.errorLength + 40]
        location = f"Line containing: \"{snippet.strip()[:100]}...\""
        grammar_issues.append(f"• {match.message} ({location})")

    tech_issues = await check_links_and_dropdowns(page, url)
    return url, grammar_issues, tech_issues

async def run_check(urls):
    async with aiohttp.ClientSession() as session:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            results = await asyncio.gather(*[
                analyze_page(url, session, page) for url in urls
            ])

            await browser.close()

    report_lines = []
    for url, grammar, tech in results:
        report_lines.append(f"# 🔍 {url}")
        if grammar:
            report_lines.append("## ✏️ Grammar/Spelling Issues:")
            report_lines.extend(grammar)
        else:
            report_lines.append("✅ No grammar issues found.")

        if tech:
            report_lines.append("## 🔧 Link/Toggle Issues:")
            report_lines.extend(tech)
        else:
            report_lines.append("✅ All links and toggles working.")

        report_lines.append("\n---\n")

    return "\n".join(report_lines)









