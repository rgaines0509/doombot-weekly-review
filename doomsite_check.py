import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import httpx

from languagetool_python import LanguageTool

tool = LanguageTool('en-US')

async def fetch_page_html(page):
    return await page.content()

async def check_links(page, url):
    errors = []
    try:
        links = await page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")
        for link in links:
            if not link.startswith("http"):
                continue
            try:
                response = httpx.get(link, timeout=10)
                if response.status_code >= 400:
                    errors.append(f"❌ Broken link: {link} (Status {response.status_code})")
            except Exception as e:
                errors.append(f"❌ Error reaching {link}: {e}")
    except Exception as e:
        errors.append(f"❌ Failed to gather links: {e}")
    return errors

async def check_tech_elements(page):
    errors = []
    try:
        dropdowns = await page.query_selector_all(".dropdown-toggle")
        for dropdown in dropdowns:
            try:
                await dropdown.click()
            except Exception:
                errors.append("❌ Dropdown toggle could not be clicked.")
    except Exception as e:
        errors.append(f"❌ Error checking dropdowns: {e}")
    return errors

def grammar_check(text):
    matches = tool.check(text)
    issues = []
    for match in matches:
        issues.append(f"• Line {match.contextoffset}: {match.message} (Suggestion: {match.replacements})")
    return issues

async def run_all_checks(url, page):
    results = [f"🌐 URL: {url}"]

    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state('networkidle')

        # Tech check
        print(f"🛠️ Tech check for {url}")
        tech_results = await check_tech_elements(page)
        if tech_results:
            results.append("🛠️ Technical Check Results:\n" + "\n".join(tech_results))
        else:
            results.append("✅ No tech issues found.")

        # Link check
        print(f"🔗 Link check for {url}")
        link_results = await check_links(page, url)
        if link_results:
            results.append("🔗 Link Check Results:\n" + "\n".join(link_results))
        else:
            results.append("✅ All links are reachable.")

        # Grammar check
        print(f"🧠 Grammar check for {url}")
        html = await fetch_page_html(page)
        soup = BeautifulSoup(html, 'html.parser')
        visible_text = soup.get_text(separator=' ', strip=True)
        grammar_issues = grammar_check(visible_text)
        if grammar_issues:
            results.append("📝 Grammar/Spelling Issues:\n" + "\n".join(grammar_issues))
        else:
            results.append("✅ No grammar issues found.")
    except Exception as e:
        results.append(f"❌ Error loading or checking page: {e}")

    return "\n".join(results)

async def run_check(urls):
    all_results = []
    print("🎯 Starting full site check...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for url in urls:
            print(f"🔍 Checking: {url}")
            try:
                result = await run_all_checks(url, page)
            except Exception as e:
                print(f"🔥 Error checking {url}: {e}")
                result = f"❌ Error on {url}: {e}"
            all_results.append(result + "\n" + "-"*50)
        await browser.close()
    return all_results






















