import asyncio
import httpx
import time
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from langdetect import detect
from language_tool_python import LanguageTool

ENABLE_GRAMMAR_CHECK = True

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
        broken_links.append(f"{url} (page l_
















