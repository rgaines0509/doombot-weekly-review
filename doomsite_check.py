import asyncio
import httpx
import time
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from langdetect import detect
from language_tool_python import LanguageTool

ENABLE_GRAMMAR_CHECK = True

SKIP_GRAMMAR_FOR = [
    "privacy-policy",
    "terms-and-conditions"
]

async def check_links(page, url):
    broken_links = []
    try:
        print(f"🔍 Starting link check: {url}")
        await page.goto(url, timeout=15000)
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
    print(f"✅ Link check done: {url} — {len(broken_links)} broken links")
    return broken_links

async def check_tech_elements(page, url):
    print(f"🛠️ Running tech check on: {url}")
    issues = []

    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_load_state('networkidle', timeout=10000)

        # Check dropdowns
        dropdowns = await page.query_selector_all(".dropdown")
        if dropdowns:
            for i, dd in enumerate(dropdowns):
                try:
                    await dd.hover()
                    await dd.click()
                except Exception:
                    issues.append(f"Dropdown #{i+1} not clickable")
        else:
            issues.append("No .dropdown elements found")

        # Check buttons
        buttons = await page.query_selector_all("button")
        if not buttons:
            issues.append("No buttons found on page")

        # Check nav
        nav = await page.query_selector(".nav")
        if not nav:
            issues.append("Navigation menu (.nav) not found")

    except Exception as e:
        issues.append(f"⚠️ Page load or JS error: {e}")

    return issues if issues else ["✅ All key UI elements passed"]

def clean_html_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

def grammar_check(text, url):
    print(f"🧠 Running grammar check on: {url}")
    try:
        lang = detect(text)
        tool = LanguageTool(lang)
        matches = tool.check(text[:20000])  # Limit grammar check to 20k chars
        print(f"✅ Grammar check complete on: {url} — {len(matches)} issues")
        issues = []
        for match in matches:
            issue = f"• Line {match.context_offset}: {match.message} — Suggestion: {', '.join(match.replacements)}"
            issues.append(issue)
        return issues
    except Exception as e:
        print(f"❌ Grammar check failed on {url}: {e}")
        return [f"⚠️ Grammar check failed: {e}"]

async def run_check(urls):
    print("🔥 Starting full site check...")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for url in urls:
            print(f"\n➡️ Processing: {url}")
            total_start = time.time()
            section = [f"🔗 URL: {url}"]

            # 🕒 Link check
            link_start = time.time()
            try:
                link_issues = await check_links(page, url)
                section.append("🔗 Link Check Results:")
                section.extend(link_issues if link_issues else ["✅ No broken links found."])
            except Exception as e:
                section.append(f"❌ Link check failed: {e}")
            link_duration = round(time.time() - link_start, 2)
            section.append(f"⏱️ Link check time: {link_duration}s")

            # 🛠️ Tech check
            tech_start = time.time()
            try:
                tech_issues = await check_tech_elements(page, url)
                section.append("🛠️ Technical Check Results:")
                section.extend(tech_issues)
            except Exception as e:
                section.append(f"⚠️ Technical check failed: {e}")
            tech_duration = round(time.time() - tech_start, 2)
            section.append(f"⏱️ Tech check time: {tech_duration}s")

            # 🧠 Grammar check
            grammar_duration = 0
            if ENABLE_GRAMMAR_CHECK and not any(skip in url for skip in SKIP_GRAMMAR_FOR):
                grammar_start = time.time()
                try:
                    await page.goto(url, timeout=15000)
                    await page.wait_for_load_state('networkidle', timeout=10000)
                    html = await page.content()
                    text = clean_html_text(html)
                    grammar_issues = grammar_check(text, url)
                    section.append("📝 Grammar/Spelling Issues:")
                    section.extend(grammar_issues if grammar_issues else ["✅ No grammar issues found."])
                except Exception as e:
                    section.append(f"⚠️ Grammar check failed for {url}: {e}")
                grammar_duration = round(time.time() - grammar_start, 2)
                section.append(f"⏱️ Grammar check time: {grammar_duration}s")
            elif not ENABLE_GRAMMAR_CHECK:
                section.append("📝 Grammar/Spelling Issues: [Disabled]")
            else:
                section.append("📝 Grammar/Spelling Issues: [Skipped for this page]")

            total_duration = round(time.time() - total_start, 2)
            print(f"✅ Finished: {url} in {total_duration}s")
            section.append(f"⏱️ Total processing time: {total_duration}s")

            results.append("\n".join(section))

        await browser.close()
        print("🏁 All pages checked.")

    return results



















