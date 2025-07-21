# 📘 Doombot Grammar & Tech Check Script (calls doombot_techcheck_v2.py)
import os
import subprocess
import httpx
from bs4 import BeautifulSoup
from language_tool_python import LanguageTool

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # unused in test mode

URLS = [
    "https://quickbookstraining.com/",
    "https://quickbookstraining.com/quickbooks-courses",
    "https://quickbookstraining.com/plans-and-pricing",
    "https://quickbookstraining.com/learn-quickbooks",
    "https://quickbookstraining.com/live-quickbooks-help",
    "https://quickbookstraining.com/quickbooks-classes",
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

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}


def fetch_page_text(url: str) -> str:
    """Fetch visible text from a page with httpx."""
    try:
        with httpx.Client(http2=True, headers=HEADERS, timeout=15, follow_redirects=True) as client:
            r = client.get(url)
            print(f"[DEBUG] {url} → {r.status_code} final={r.url}")
            r.raise_for_status()
            return BeautifulSoup(r.text, "lxml").get_text(" ", strip=True)
    except Exception as e:
        return f"[Fetch error: {e}]"


def run_grammar_checks() -> str:
    tool = LanguageTool("en-US")
    parts = ["🧠 *Doombot Grammar Report*"]
    for u in URLS:
        txt = fetch_page_text(u)
        matches = tool.check(txt)
        parts.append(f"\n🔗 {u}")
        if not matches:
            parts.append("✅ No grammar issues found.")
            continue
        for m in matches[:5]:
            err = txt[m.offset:m.offset + m.errorLength]
            sug = m.replacements[0] if m.replacements else "(no suggestion)"
            parts.append(f"❌ {m.ruleIssueType.capitalize()}: “{err}” → “{sug}”")
    return "\n".join(parts)


def run_tech_check() -> str:
    print("🧪 Running doombot_techcheck_v2.py …")
    result = subprocess.run(["python", "doombot_techcheck_v2.py"], capture_output=True, text=True)
    return result.stdout or result.stderr


if __name__ == "__main__":
    full_report = run_grammar_checks() + "\n\n" + run_tech_check()
    print(full_report)
    print("🚫 Slack disabled for test run.")



