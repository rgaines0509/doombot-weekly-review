import asyncio
import time
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import httpx
from language_tool_python import LanguageTool  # ✅ Correct import

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
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_timeout(2000)  # short buffer after DOM is loaded

        # TECH CHECK
        print(f"🛠️ Starting tech check for {url}")
        try:
            start = time.time()
            tech_results = await asyncio.wait_for(check_tech_elements(page), timeout=60)
            print(f"✅ Tech check completed in {time.time() - start:.2f}s")
            if tech_results:
                results.append("🛠️ Technical Check Results:\n" + "\n".join(tech_results))
            else:
                results.append("✅ No tech issues found.")
        except asyncio.TimeoutError:
            print("❌ Tech check timed out.")
            results.append("❌ Tech check timed out.")

        # LINK CHECK
        print(f"🔗 Starting link check for {url}")
        try:
            start = time.time()
            link_results = await asyncio.wait_for(check_links(page, url), timeout=60)
            print(f"✅ Link check completed in {time.time() - start:.2f}s")
            if link_results:
                results.append("🔗 Link Check Results:\n" + "\n".join(link_results))
            else:
                results.append("✅ All links are reachable.")
        except asyncio.TimeoutError:
            print("❌ Link check timed out.")
            results.append("❌ Link check timed out.")

        # GRAMMAR CHECK
        print(f"🧠 Starting grammar check for {url}")
        try:
            start = time.time()
            html = await fetch_page_html(page)
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script/style tags
            for tag in soup(['script', 'style']):
                tag.decompose()

            visible_text = soup.get_text(separator=' ', strip=True)
            visible_text = visible_text[:15000]  # Cap grammar input length

            grammar_issues = await asyncio.get_event_loop().run_in_executor(
                None, grammar_check, visible_text
            )

            print(f"✅ Grammar check completed in {time.time() - start:.2f}s")
            if grammar_issues:
                results.append("📝 Grammar/Spelling Issues:\n" + "\n".join(grammar_issues))
            else:
                results.append("✅ No grammar issues found.")
        except asyncio.TimeoutError:
            print("❌ Grammar check timed out.")
            results.append("❌ Grammar check timed out.")

    except Exception as e:
        results.append(f"❌ Error loading or checking page: {e}")

    return "\n".join(results)

async def run_check(urls):
    all_results = []
    print("🎯 Starting full site check...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for url in urls:
            page = await browser.new_page()
            print(f"🔍 Checking: {url}")
            try:
                result = await run_all_checks(url, page)
            except Exception as e:
                print(f"🔥 Error checking {url}: {e}")
                result = f"❌ Error on {url}: {e}"
            all_results.append(result + "\n" + "-"*50)
            await page.close()
        await browser.close()
    return all_results


























