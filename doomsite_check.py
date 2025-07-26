import asyncio
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from langdetect import detect
from language_tool_python import LanguageTool

ENABLE_GRAMMAR_CHECK = True

async def check_links(page, url):
    broken_links = []
    try:
        await page.goto(url, timeout=15000)
        print(f"🔍 Checking links on: {url}")
        await page.wait_for_load_state('networkidle', timeout=10000)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        anchors = soup.find_all('a', href=True)
        for anchor in anchors:
            href = anchor['href']
            if href.startswith("mailto:") or href.startswith("tel:"):
                continue
            try:
                full_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                    r = await client.get(full_url)
                    if r.status_code >= 400:
                        broken_links.append(f"{full_url} → Status {r.status_code}")
            except Exception as e:
                broken_links.append(f"{href} → ERROR: {e}")
    except Exception as e:
        broken_links.append(f"{url} (page load error): {e}")
    return broken_links

def clean_html_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

def grammar_check(text):
    print("🧠 Running grammar check...")
    try:
        lang = detect(text)
        tool = LanguageTool(lang)
        matches = tool.check(text[:20000])  # Limit to first 20K characters
        issues = []
        for match in matches:
            issue = f"• Line {match.context_offset}: {match.message} — Suggestion: {', '.join(match.replacements)}"
            issues.append(issue)
        return issues
    except Exception as e:
        return [f"⚠️ Grammar check failed: {e}"]

async def run_check(urls):
    print("🔥 Starting full site check...")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for url in urls:
            section = [f"🔗 URL: {url}"]

            try:
                link_issues = await check_links(page, url)
                section.append("🔗 Link Check Results:")
                section.extend(link_issues if link_issues else ["✅ No broken links found."])
            except Exception as e:
                section.append(f"❌ Link check failed: {e}")

            if ENABLE_GRAMMAR_CHECK:
                try:
                    await page.goto(url, timeout=15000)
                    await page.wait_for_load_state('networkidle', timeout=10000)
                    html = await page.content()
                    text = clean_html_text(html)
                    grammar_issues = grammar_check(text)
                    section.append("📝 Grammar/Spelling Issues:")
                    section.extend(grammar_issues if grammar_issues else ["✅ No grammar issues found."])
                except Exception as e:
                    section.append(f"⚠️ Grammar check failed for {url}: {e}")

            results.append("\n".join(section))
            print(f"✅ Completed: {url}")

        await browser.close()
        print("🏁 All pages checked.")

    return results














