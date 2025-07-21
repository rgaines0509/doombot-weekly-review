# 📘 Doombot Grammar & Tech Check Script (No Slack)
import os
import requests
import subprocess
from bs4 import BeautifulSoup
from language_tool_python import LanguageTool

# Slack webhook is loaded but unused
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

URLS = [
    "https://quickbookstraining.com/",
    "https://quickbookstraining.com/quickbooks-courses",
    "https://quickbookstraining.com/plans-and-pricing"
]

def fetch_page_text(url):
    try:
        res = requests.get(url, timeout=10, headers={'User-Agent': 'Doombot/1.0'})
        soup = BeautifulSoup(res.text, 'lxml')
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        return f"[Error fetching page: {e}]"

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
        for match in matches[:5]:  # Limit for readability
            error_text = content[match.offset:match.offset + match.errorLength]
            suggestion = match.replacements[0] if match.replacements else "(no suggestion)"
            context = content[max(0, match.offset - 40):match.offset + match.errorLength + 40]
            context = context.replace("\n", " ").replace(error_text, f"*{error_text}*")
            output.append(f"❌ {match.ruleIssueType.capitalize()}: “{error_text}” ➝ “{suggestion}”\n💬 Context: …{context}…")
    return "\n".join(output)

def run_tech_check():
    try:
        result = subprocess.run(["python", "tech_check.py"], capture_output=True, text=True, check=True)
        return f"\n🛠️ *Doombot Tech Check Output:*\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"\n⚠️ Tech Check Failed:\n{e.output or e.stderr}"

if __name__ == "__main__":
    grammar_report = run_grammar_checks()
    tech_report = run_tech_check()
    full_report = f"{grammar_report}\n\n{tech_report}"

    print(full_report)  # Only prints to GitHub Actions log

    # Do NOT post to Slack in this test version
    print("\n🚫 Slack post disabled for test run.")






