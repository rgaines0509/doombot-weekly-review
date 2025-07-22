# 📘 Doombot Grammar & Tech Check Script (with httpx, safe test version)
import os
import subprocess
import httpx
from bs4 import BeautifulSoup
from language_tool_python import LanguageTool

# Slack webhook is loaded but unused for this version
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

URLS = [
    "https://quickbookstraining.com/",
    "https://quickbookstraining.com/quickbooks-courses",
    "https://quickbookstraining.com/plans-and-pricing"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

def fetch_page_text(url):
    try:
        with httpx.Client(http2=True, headers=HEADERS, timeout=10, follow_redirects=True) as client:
            res = client.get(url)
            print(f"[DEBUG] {url} - Status: {res.status_code} - Final URL: {res.url}")
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "lxml")
            return soup.get_text(separator=" ", strip=True)
    except httpx.RequestError as e:
        print(f"[ERROR] Request failed for {url}: {e}")
        return f"[Error fetching page: {e}]"
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] HTTP error for {url}: {e.response.status_code}")
        return f"[HTTP error fetching page: {e.response.status_code}]"

def run_grammar_checks():
    tool = LanguageTool('en-US')
    output = ["🧠 *Doombot Grammar Report*"]

    for url in URLS:
        content = fetch_page_text(url)
        matches = tool.check(content)
        output.append(f"\n🔗 {url}")
        if not matches:
            output.append("✅ No grammar issues found.")
            continue
        for match in matches[:5]:
            error_text = content[match.offset:match.offset + match.errorLength]
            suggestion = match.replacements[0] if match.replacements else "(no suggestion)"
            context = content[max(0, match.offset - 40):match.offset + match.errorLength + 40]
            context = context.replace("\n", " ").replace(error_text, f"*{error_text}*")
            output.append(f"❌ {match.ruleIssueType.capitalize()}: “{error_text}” ➝ “{suggestion}”\n💬 Context: …{context}…")
    return "\n".join(output)

def run_tech_check():
    try:
        result = subprocess.run(["python", "tech_check_v2.py"], capture_output=True, text=True, check=True)
        return f"\n🛠️ *Doombot Tech Check Output:*\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"\n⚠️ Tech Check Failed:\n{e.output or e.stderr}"

if __name__ == "__main__":
    grammar_report = run_grammar_checks()
    tech_report = run_tech_check()
    full_report = f"{grammar_report}\n\n{tech_report}"

    print(full_report)  # Logs to GitHub Actions output
    print("\n🚫 Slack post disabled for test run.")








