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
        f"Version: DoomCheck v2025.07.23",
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

        # Dropdown toggle results
        if res["dropdowns"]:
            failed = res["dropdowns"].count("Fail")
            total = len(res["dropdowns"])
            lines.append(f"📂 Dropdowns tested: {total}, Passed: {total - failed}, Failed: {failed}")
        else:
            lines.append("ℹ️ No dropdowns found on this page.")

        # Grammar & spelling
        if res["grammar_errors"]:
            lines.append("📝 **Grammar/Spelling Issues:**")
            for err in res["grammar_errors"]:
                lines.append(f"- {err}")
        else:
            lines.append("✅ No grammar or spelling issues found.")

    return "\n".join(lines)

async def main():
    print("🧠 DoomCheck v2025.07.23 — This is the NEW main.py running.")
    results = await run_check(URLS_TO_CHECK)
    report_text = format_report(results)

    with open("weekly_report.md", "w", encoding="utf-8") as f:
        f.write(report_text)

    print("✅ Weekly report generated: weekly_report.md")

if __name__ == "__main__":
    asyncio.run(main())


