import asyncio
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from langdetect import detect
from language_tool_python import LanguageTool
import re

# Grammar checking remains ON
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
                async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                    r = await client.get(href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/"))
                    if r.status_code >= 400:
                        broken_links.append(f"{href} -> Status {r.status_code}")
            except Exception as e:
                broken_links.append(f"{href} -> ERROR: {str(e)}")
    except Exception as e:
        broken_links.append(f"{url} (page load error): {str(e)}")
    return broken_links

def clean_html_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(["script", "style", "noscript"]):
        script.extract()
    return soup.get_text(separator=" ", strip=True)

def grammar_check(text):
    print("🧠 Starting grammar check...")
    try:
        lang = detect(text)
        print(f"🌐 Detected language: {lang}")
        tool = LanguageTool(lang)
        matches = tool.check(text[:20000])  # Cap check to 20k characters
        print(f"✅ Grammar check complete. Found {len(matches)} issues.")
        issues = []
        for match in matches:
            issue = f"• Line {match.context_offset}: {match.message} — Suggestion: {', '.join(match.replacements)}"
            issues.append(issue)
        return issues
    except Exception as e:
        print(f"❌ Grammar check failed: {e}")
        return ["⚠️ Grammar check failed."]

async def run_check(urls):
    print("🔥 run_check() started")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for url in urls:
            print(f"➡️ Visiting: {url}")
            section = [f"🔗 URL: {url}"]

            try:
                link_issues = await check_links(page, url)
                section.append("🔗 Broken Links:")













