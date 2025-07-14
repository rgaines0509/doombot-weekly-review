# 📘 Doombot Grammar & Continuity Review Script
# Enhanced with location-level context and formatting for Slack

import os
import requests
import asyncio
from language_tool_python import LanguageTool
from playwright.async_api import async_playwright

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

PAGES = {
    "https://quickbookstraining.com/": "Home page content here...",
    "https://quickbookstraining.com/quickbooks-courses": "Courses page content here...",
    "https://quickbookstraining.com/plans-and-pricing": "Pricing page content here..."
    # Add more pages and HTML/text content here
}

URLS = list(PAGES.keys())

def get_surrounding_text(text, error_offset, length, radius=40):
    start = max(0, error_offset - radius)
    end = min(len(text), error_offset + length + radius)
    return text[start:end].replace("\n", " ").strip()

def run_grammar_checks():
    tool = LanguageTool('en-US')
    final_results = ["\U0001f4dd *Doombot Grammar Report*\n"]

    for url, content in PAGES.items():
        matches = tool.check(content)
        if not matches:
            final_results.append(f"✅ {url} - No grammar or spelling issues found.")
            continue

        final_results.append(f"🔎 {url}")
        for match in matches:
            issue_type = match.ruleIssueType.capitalize()
            error_text = content[match.offset:match.offset + match.errorLength]
            suggestion = match.replacements[0] if match.replacements else "(no suggestion)"
            context = get_surrounding_text(content, match.offset, match.errorLength)
            highlighted = context.replace(error_text, f"*{error_text}*")
            final_results.append(f"❌ {issue_type}: “{error_text}” ➝ Suggested: “{suggestion}”\n🧠 Context: “…{highlighted}…”")

    return "\n\n".join(final_results)

async def run_tech_checks():
    results = ["\n\n\U0001f4bb *Doombot UI & Tech Check Results*\n"]
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
                    page_report.append("✅ Dropdown clickable")
                else:
                    page_report.append("⚠️ Dropdown not found")

                links = await page.query_selector_all("a")
                if not links:
                    page_report.append("⚠️ No links found")
            except Exception as e:
                page_report.append(f"❌ Error loading page: {e}")

            if console_errors:
                page_report.append(f"❌ Console Errors: {console_errors}")
            else:
                page_report.append("✅ No console errors found")

            results.append("\n".join(page_report))

        await browser.close()
    return "\n\n".join(results)

async def main():
    grammar_report = run_grammar_checks()
    tech_report = await run_tech_checks()

    final_report = f"{grammar_report}\n{tech_report}"
    print(final_report)

    with open("combined_report.txt", "w", encoding="utf-8") as f:
        f.write(final_report)

    if SLACK_WEBHOOK_URL:
        try:
            slack_payload = {"text": final_report[:3500]}
            res = requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
            if res.status_code == 200:
                print("\n✅ Combined report sent to Slack.")
            else:
                print(f"\n⚠️ Slack error: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"\n⚠️ Failed to send report to Slack: {e}")
    else:
        print("\n⚠️ Slack webhook not configured.")

if __name__ == "__main__":
    asyncio.run(main())

