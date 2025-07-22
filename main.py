# 📘 Doombot Grammar + Tech Check (Final, all URLs, Slack disabled)

import subprocess
import httpx
from bs4 import BeautifulSoup
from language_tool_python import LanguageTool

# ── 1.  Full list of pages to scan ──────────────────────────────────────────
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
    "https://quickbookstraining.com/privacy-policy",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

# ── 2.  Helpers ─────────────────────────────────────────────────────────────
def fetch_page_text(url: str) -> str:
    """Return visible text from URL or an error string."""
    try:
        with httpx.Client(http2=True, headers=HEADERS, timeout=10, follow_redirects=True) as c:
            r = c.get(url)
            print(f"[DEBUG] {url} → {r.status_code} (final {r.url})")
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")
            return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        return f"[Error fetching page: {e}]"

def run_grammar_checks() -> str:
    tool = LanguageTool("en-US")
    report = ["🧠 *Doombot Grammar Report*"]

    for url in URLS:
        text = fetch_page_text(url)
        matches = tool.check(text)
        report.append(f"\n🔗 {url}")
        if not matches:
            report.append("✅ No grammar issues found.")
            continue
        for m in matches[:5]:  # limit per page
            snippet = text[m.offset : m.offset + m.errorLength]
            suggestion = m.replacements[0] if m.replacements else "(no suggestion)"
            context = text[max(0, m.offset - 40) : m.offset + m.errorLength + 40].replace(
                snippet, f"*{snippet}*"
            )
            report.append(
                f"❌ {m.ruleIssueType.capitalize()}: “{snippet}” ➝ “{suggestion}”\n"
                f"💬 Context: …{context}…"
            )
    return "\n".join(report)

def run_tech_check() -> str:
    """Call the NEW tech-check script."""
    try:
        res = subprocess.run(
            ["python", "tech_check_v2.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        return f"\n🛠️ *Doombot Tech Check Output*:\n{res.stdout}"
    except subprocess.CalledProcessError as e:
        return f"\n⚠️ Tech check failed:\n{e.stdout or e.stderr}"

# ── 3.  Entry point ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    full_report = f"{run_grammar_checks()}\n\n{run_tech_check()}"
    print(full_report)                    # shows in GitHub-Actions logs
    print("\n🚫 Slack posting is OFF for this test run.")









