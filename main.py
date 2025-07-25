import asyncio
from datetime import datetime
from doomsite_check import run_check


def format_report(sections):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"# 🧒 Doombot Weekly Website Review\n\n**Generated:** {timestamp}\n\n"
    return header + "\n".join(sections)


async def main():
    print("\ud83d\ude80 Doombot Report Starting...")
    results = await run_check([
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
    ])

    markdown = format_report(results)
    with open("weekly_report.md", "w", encoding="utf-8", errors="ignore") as f:
    f.write(markdown)


    print("\u2705 weekly_report.md written. Doombot Check Complete.")


if __name__ == "__main__":
    asyncio.run(main())









