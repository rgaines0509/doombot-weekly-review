import aiohttp
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright

# No grammar analysis for now; built-in placeholder if needed
def dummy_grammar_check(text):
    return []

async def fetch_html(session, url):
    try:
        async with session.get(url, timeout=20) as response:
            return await response.text(), None
    except Exception as e:
        return None, str(e)

def extract_visible_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for script_or_style in soup(["script", "style", "noscript"]):
        script_or_style.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def extract_links_and_dropdowns(html):
    soup = BeautifulSoup(html, "html.parser")
    links = [a['href'] for a in soup.find_all('a', href=True)]
    dropdowns = soup.select("details, .dropdown, [aria-haspopup='true']")
    return links, dropdowns

async def check_link(session, base_url, link):
    if link.startswith("mailto:") or link.startswith("tel:") or link.startswith("#"):
        return None
    if link.startswith("/"):
        link = base_url.rstrip("/") + link
    elif not link.startswith("http"):
        return None

    try:
        async with session.get(link, timeout=10) as response:
            if response.status >= 400:
                return (link, response.status)
    except Exception:
        return (link, "Request Failed")
    return None

async def check_dropdowns(playwright, url):
    results = []
    try:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=20000)
        dropdowns = await page.query_selector_all("details, .dropdown, [aria-haspopup='true']")
        for dropdown in dropdowns:
            try:
                await dropdown.click()
                results.append("Pass")
            except Exception:
                results.append("Fail")
        await browser.close()
    except Exception:
        results.append("Fail")
    return results

async def analyze_page(session, playwright, url):
    html, error = await fetch_html(session, url)
    if error:
        return f"## 🔗 {url}\n❌ Error loading page: {error}\n"

    text = extract_visible_text(html)
    links, dropdowns = extract_links_and_dropdowns(html)

    # Check links
    broken_links = []
    link_checks = await asyncio.gather(*[
        check_link(session, url, link) for link in links
    ])
    broken_links = [result for result in link_checks if result]

    # Check dropdowns
    dropdown_results = await check_dropdowns(playwright, url)

    # Check grammar (dummy for now)
    grammar_errors = dummy_grammar_check(text)

    # Start building formatted report string
    report = [f"## 🔗 {url}"]

    if broken_links:
        report.append("🚨 **Broken Links:**")
        for link, code in broken_links:
            report.append(f"- {link} (status: {code})")
    else:
        report.append("✅ No broken links found.")

    if dropdown_results:
        failed = dropdown_results.count("Fail")
        total = len(dropdown_results)
        report.append(f"📂 Dropdowns: **{total} tested**, ✅ {total - failed} passed, ❌ {failed} failed")
    else:
        report.append("ℹ️ No dropdowns found.")

    if grammar_errors:
        report.append("📝 **Grammar/Spelling Issues:**")
        for err in grammar_errors:
            report.append(f"- {err}")
    else:
        report.append("✅ No grammar/spelling issues found.")

    return "\n".join(report)

async def run_check(urls):
    async with aiohttp.ClientSession() as session:
        async with async_playwright() as playwright:
            tasks = [analyze_page(session, playwright, url) for url in urls]
            return await asyncio.gather(*tasks)











