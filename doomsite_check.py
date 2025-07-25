import aiohttp
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import language_tool_python

# Initialize the grammar checker
tool = language_tool_python.LanguageTool('en-US')

# Runs grammar check and returns formatted list of issues
def grammar_check(text):
    matches = tool.check(text)
    if not matches:
        return ["✅ No grammar or spelling issues found."]

    issues = []
    for match in matches:
        context = text[max(0, match.offset - 30):match.offset + match.errorLength + 30].replace("\n", " ")
        issues.append(f"❌ *{match.message}*\nSuggestion: `{match.replacements}`\nContext: _...{context.strip()}..._\n")
    return issues

# Check all links and toggles on the page
def validate_links_and_toggles(soup, url):
    issues = []

    # Check links
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
        issues.append(f"🔗 Found link: {href}")

    # Check dropdown toggles
    toggles = soup.select('[data-toggle], .dropdown-toggle')
    if toggles:
        for toggle in toggles:
            issues.append(f"⬇️ Found dropdown toggle: {str(toggle)[:100]}...")
    else:
        issues.append("⚠️ No dropdown toggles found on this page.")

    return issues

# Scrape content and validate
async def fetch_and_check(page, url):
    await page.goto(url, wait_until="networkidle")
    html = await page.content()
    soup = BeautifulSoup(html, 'html.parser')

    # Extract visible text for grammar check
    visible_text = soup.get_text(separator=' ', strip=True)
    grammar_issues = grammar_check(visible_text)
    tech_issues = validate_links_and_toggles(soup, url)

    report = f"\n==============================\n🔍 Review for: {url}\n==============================\n"
    report += "\n**🔤 Grammar & Spelling:**\n" + "\n".join(grammar_issues)
    report += "\n\n**🛠️ Tech Check (Links & Toggles):**\n" + "\n".join(tech_issues)
    return report

# Master run function
def run_check(urls):
    async def inner():
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            for url in urls:
                try:
                    result = await fetch_and_check(page, url)
                    results.append(result)
                except Exception as e:
                    results.append(f"❌ Error checking {url}: {str(e)}")

            await browser.close()
        return results
    return asyncio.run(inner())










