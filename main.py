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
    "https://quickbookstraining.com/privacy-policy"
]

def format_report(results):
    lines = [
        f"# 🧾 Doombot Weekly Website Review",
        f"Version: DoomCheck v2025.07.23 (no grammar, no Playwright)",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    ]

    for res in results:
        lines.append(f"\n---\n## 🔗 URL: {res['url']}")

        if "error" in res:
            lines.append(f"❌ Error loading page: {res['error']}")
            continue

        # Broken links
        if res["broken_links"]:
            lines.append("🚨 **Broken Links Found:**")
            for link, code in res["broken_links"]:
                lines.append(f"- {link} (status: {code})")
        else:
            lines.append("✅ No broken links found.")

        # Dropdown results
        if res["dropdowns"]:
            lines.append("📂 Dropdown-like elements detected:")
            for d in res["dropdowns"]:
                lines.append(f"- {d}")
        else:
            lines.append("ℹ️ No dropdown-style elements found.")

        # Grammar/skipped notes
        if res["grammar_errors"]:
            lines.append("📝 **Grammar/Spelling Status:**")
            for err in res["grammar_errors"]:
                lines.append(f"- {err}")
        else:
            lines.append("✅ No grammar/spelling notes reported.")

    return "\n".join(lines)

async def main():
    print("🚀 Doombot Report Starting (No grammar, no Playwright)...")

    results = await run_check(URLS_TO_CHECK)

    print("📊 Report generated, writing to file...")

    report_text = format_report(results)

    with open("weekly_report.md", "w", encoding="utf-8") as f:
        f.write(report_text)

    print("✅ weekly_report.md written. Doombot Check Complete.")

if __name__ == "__main__":
    asyncio.run(main())


