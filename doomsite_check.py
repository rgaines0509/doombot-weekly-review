import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
import language_tool_python

tool = language_tool_python.LanguageTool('en-US')

MAX_TEXT_LENGTH = 20000  # cap to ~20K characters
GRAMMAR_TIMEOUT_SEC = 20  # limit grammar check time

async def check_page(page, url):
    print(f"\n🧪 Checking: {url}")
    await page.goto(url, wait_until="networkidle")

    # Collect all links
    links = await page.eval_on_selector_all("a[href]", "elements => elements.map(el => el.href)")
    broken_links = []

    for link in links:
        try:
            res = requests.get(link, timeout=5)
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

    # Grab visible text
    html = await page.content()
    soup = BeautifulSoup(html, "lxml")
    visible_text = ' '.join([el.get_text(strip=True) for el in soup.find_all(['p', 'li', 'span', 'div', 'h1', 'h2', 'h3'])])
    visible_text = visible_text.strip()

    grammar_errors = []
    if visible_text and len(visible_text) < MAX_TEXT_LENGTH:
        try:
            print(f"🔍 Running grammar check for: {url}")
            matches = await asyncio.wait_for(
                asyncio.to_thread(tool.check, visible_text),
                timeout=GRAMMAR_TIMEOUT_SEC
            )
            for match in matches:
                context = match.context[:75].strip().replace('\n', ' ')
                grammar_errors.append(f"✏️ Issue: {match.message}\n   ➤ Suggestion: {match.replacements}\n   🔍 Location: {context}")
        except asyncio.TimeoutError:
            grammar_errors.append("⚠️ Grammar check timed out on this page.")
        except Exception as e:
            grammar_errors.append(f"⚠️ Grammar check failed: {str(e)}")
    elif not visible

