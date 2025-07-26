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

    try:
        results = await asyncio.wait_for(run_check(URLS_TO_CHECK), timeout=300)
    except asyncio.TimeoutError:
        safe_print("❌ Timeout: Website check took longer than 5 minutes.")
        results = ["⚠️ ERROR: The website chec]()












