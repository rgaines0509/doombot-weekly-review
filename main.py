import asyncio
from datetime import datetime
from doomsite_check import run_check

URLS_TO_CHECK = [
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

def format_markdown(report_sections):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = [f"# 🧾 Doombot Weekly Website Review", f"**Generated:** {timestamp}", ""]
    for section in report_sections:
        output.append(section)
    return "\n".join(output)

async def main():
    print("🚀 Doombot Report Starting (Markdown only)...")
    results = await run_check(URLS_TO_CHECK)

    report_md = format_markdown(results)

    with open("weekly_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print("✅ weekly_report.md written. Doombot Check Complete.")

if __name__ == "__main__":
    asyncio.run(main())








