import asyncio
from datetime import datetime
from doomsite_check import run_check

# ⏱️ Change this to test fewer pages faster
URL_LIMIT = 2

# 🔗 Full site URL list — edit only if you add new pages
ALL_URLS = [
    "https://quickbookstraining.com/",
    "https://quickbookstraining.com/live-quickbooks-help",
    "https://quickbookstraining.com/quickbooks-courses",
    "https://quickbookstraining.com/quickbooks-classes",
    "https://quickbookstraining.com/plans-and-pricing",
    "https://quickbookstraining.com/about-us",
    "https://quickbookstraining.com/contact-us",
    "https://quickbookstraining.com/quickbooks-certification",
    "https://quickbookstraining.com/quickbooks-online-certification",
    "https://quickbookstraining.com/quickbooks-desktop-certification",
    "https://quickbookstraining.com/quickbooks-bookkeeping-certification",
    "https://quickbookstraining.com/quickbooks-certification-online",
    "https://quickbookstraining.com/quickbooks-certification-exam",
    "https://quickbookstraining.com/terms-and-conditions",
    "https://quickbookstraining.com/privacy-policy",
    "https://quickbookstraining.com/learn-quickbooks"
]

# 🎯 Throttle number of URLs for speed
URLS_TO_CHECK = ALL_URLS[:URL_LIMIT]

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("utf-8", "replace").decode("utf-8"))

def format_report(sections):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"🧾 Doombot Weekly Website Review\nGenerated: {timestamp}\n\n"
    return header + "\n".join(sections)

async def main():
    safe_print("🚀 Doombot Report Starting...")
    safe_print(f"🔗 Checking {len(URLS_TO_CHECK)} pages...")

    try:
        results = await asyncio.wait_for(run_check(URLS_TO_CHECK), timeout=300)
    except asyncio.TimeoutError:
        safe_print("❌ Timeout: Website check took longer than 5 minutes.")
        results = ["⚠️ ERROR: The website check timed out after 5 minutes."]
    except Exception as e:
        safe_print(f"❌ UNEXPECTED ERROR during run_check: {e}")
        results = [f"⚠️ Fatal error while running checks: {e}"]

    markdown = format_report(results)

    try:
        safe_print("💾 Generating weekly_report.md...")
        with open("weekly_report.md", "w", encoding="utf-8", errors="ignore") as f:
            f.write(markdown)
        safe_print("✅ Report saved successfully.")
    except Exception as e:
        safe_print(f"❌ FAILED to save weekly_report.md: {e}")

if __name__ == "__main__":
    asyncio.run(main())














