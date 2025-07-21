# 📘 Doombot Grammar & Continuity Review Script
# Live content + Slack integration

import os
import requests
from bs4 import BeautifulSoup
from language_tool_python import LanguageTool

# 🌐 URLs to scan
URLS = [
    "https://quickbookstraining.com/",
    "https://quickbookstraining.com/quickbooks-courses",
    "https://quickbookstraining.com/plans-and-pricing",
    "https://quickbookstraining.com/live-quickbooks-help",
    "https://quickbookstraining.com/quickbooks-classes",
    "https://quickbookstraining.com/about-us",
    "https://quickbookstraining.com/contact-us",
    "https://quickbookstraining.com/quickbooks-certification",
    "https://quickbookstraining.com/quickbooks-online-certification",
    "https://quickbookstraining.com/quickbooks-bookkeeping-certification",
    "https://quickbookstraining.com/quickbooks-certification-online",
    "https://quickbookstraining.com/terms-and-conditions",
    "https://quickbookstraining.com/privacy-policy",
    "https://quickbookstraining.com/learn-quickbooks",
    "https://quickbookstraining.com/quickbooks-certification-exam"
    
]

# 🚨 Slack Webhook (set in GitHub Secrets or .env)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# 🧠 Get visible text from a page
def fetch_page_text(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Doombot/1.0"})
        soup = BeautifulSoup(response.text, "lxml")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        return f"(Error fetching page: {e})"

# 🔍 Context window for flagged errors
def get_surrounding_text(text, error_offset, length, radius=40):
    start = max(0, error_offset - radius)
    end = min(len(text), error_offset + length + radius)
    return text[start:end].replace("\n", " ").strip()

# ✏️ Grammar analysis
def run_grammar_checks():
    tool = LanguageTool('en-US')
    final_results = ["📝 *Doombot Grammar Report*\n"]

    for url in URLS:
        text = fetch_page_text(url)
        matches = tool.check(text)

        if not matches:
            final_results.append(f"✅ {url} — No grammar or spelling issues found.")
            continue

        final_results.append(f"🔎 {url}")
        for match in matches[:8]:  # Limit to 8 per page for brevity
            issue_type = match.ruleIssueType.capitalize()
            error_text = text[match.offset:match.offset + match.errorLength]
            suggestion = match.replacements[0] if match.replacements else "(no suggestion)"
            context = get_surrounding_text(text, match.offset, match.errorLength)
            highlighted = context.replace(error_text, f"*{error_text}*")
            final_results.append(
                f"❌ {issue_type}: “{error_text}” ➝ Suggested: “{suggestion}”\n"
                f"🧠 Context: “…{highlighted}…”"
            )

    report = "\n\n".join(final_results)
    print(report)

    # 🧾 Save to local file (optional)
    with open("grammar_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    # 🚀 Send to Slack
    if SLACK_WEBHOOK_URL:
        try:
            slack_payload = {"text": report[:3500]}  # Slack max limit
            res = requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
            if res.status_code == 200:
                print("\n✅ Grammar report sent to Slack.")
            else:
                print(f"\n⚠️ Slack error: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"\n⚠️ Failed to send report to Slack: {e}")
    else:
        print("\n⚠️ Slack webhook not configured.")

if __name__ == "__main__":
    run_grammar_checks()




