# 📦 Doombot Tech Check - Playwright Script (Option B)
# Checks dropdowns, link clicks, and console errors

import os
import asyncio
import requests
from playwright.async_api import async_playwright

URLS = [
    "https://quickbookstraining.com/",
    "https://quickbookstraining.com/quickbooks-courses",
    "https://quickbookstraining.com/plans-and-pricing",
    # Add more URLs as needed
]

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

async def run_tech_checks():
    results = ["\U0001f4bb *Doombot UI & Tech Check Results*\n"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        for url in URLS:
            page_report = [f"🔍 {url}"]
            page = await context.new_page()
            console_errors = []

            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            try:
                await page.goto(url, timeout=20000)

                toggle = await page.query_selector(".dropdown-toggle")
                if toggle:
                    await toggle.click()
                    dropdown_visible = await page.is_visible(".dropdown-menu")
                    if dropdown_visible:
                        page_report.append("✅ Dropdown opened successfully")
                    else:
                        page_report.append("❌ Dropdown did not open after click")
                else:
                    page_report.append("⚠️ No .dropdown-toggle element found")

                links = await page.query_selector_all("a")
                for link in links[:10]:
                    href = await link.get_attribute("href")
                    try:
                        await link.scroll_into_view_if_needed()
                        await link.hover()
                        page_report.append(f"✅ Link hover test passed: {href}")
                    except:
                        page_report.append(f"❌ Link not interactable: {href}")

                if console_errors:
                    page_report.append("❌ Console errors found:")
                    for err in console_errors[:3]:
                        page_report.append(f"  - {err}")
                else:
                    page_report.append("✅ No JavaScript errors detected")

            except Exception as e:
                page_report.append(f"❌ Error loading page: {e}")

            results.append("\n".join(page_report))
            await page.close()

        await browser.close()

    final_report = "\n\n".join(results)
    print(final_report)

    # Combine with grammar report
    grammar_path = "grammar_report.txt"
    grammar_text = ""
    if os.path.exists(grammar_path):
        with open(grammar_path, "r", encoding="utf-8") as f:
            grammar_text = f.read()

    combined = f"*🧠 Doombot Grammar Report*
{grammar_text}\n\n{final_report}"

    if SLACK_WEBHOOK_URL:
        slack_payload = {"text": combined[:3500]}
        try:
            slack_response = requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
            if slack_response.status_code == 200:
                print("\n✅ Combined report sent to Slack.")
            else:
                print(f"\n⚠️ Slack error: {slack_response.status_code} - {slack_response.text}")
        except Exception as slack_error:
            print(f"\n⚠️ Failed to send to Slack: {slack_error}")
    else:
        print("\n⚠️ Slack webhook URL not set. Report printed only.")

if __name__ == "__main__":
    asyncio.run(run_tech_checks())

Add tech_check.py for UI and console testing
