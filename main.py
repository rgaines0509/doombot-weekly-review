# 📦 Doombot Weekly Website Review - Render Version (No Colab Shell Commands)

import os
import requests
from bs4 import BeautifulSoup
import language_tool_python

# 📝 URLs to check manually
URLS = [
    "https://quickbookstraining.com/live-quickbooks-help",
    "https://quickbookstraining.com/quickbooks-courses",
    "https://quickbookstraining.com/",
    "https://quickbookstraining.com/quickbooks-classes",
    "https://quickbookstraining.com/plans-and-pricing",
    "https://quickbookstraining.com/about-us",
    "https://quickbookstraining.com/contact-us",
    "https://quickbookstraining.com/quickbooks-certification",
    "https://quickbookstraining.com/quickbooks-online-certification",
    "https://quickbookstraining.com/quickbooks-bookkeeping-certification",
    "https://quickbookstraining.com/quickbooks-certification-online",
    "https://quickbookstraining.com/terms-and-conditions",
    "https://quickbookstraining.com/privacy-policy"
]

# 📤 Slack webhook URL (replace with your actual webhook if needed)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # Set in Render's environment variables

# 🧠 Grammar check each page
def check_page_grammar(url, tool):
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Doombot/1.0'})
        soup = BeautifulSoup(response.text, 'lxml')
        text = soup.get_text(separator=' ', strip=True)
        matches = tool.check(text)
        bullet_points = []
        if not matches:
            bullet_points.append("- No issues found 🎉")
        for match in matches[:10]:
            bullet_points.append(f"- {match.message} | Suggestion: {match.replacements[:2]}")
        return f"\n🔍 {url}\n" + "\n".join(bullet_points)
    except Exception as e:
        return f"\n🔍 {url}\n- Error: {e}"

# ▶️ Run the checks and collect the full report
tool = language_tool_python.LanguageTool('en-US')
report_lines = [f"🕵️ Doombot Website Grammar Check\nChecked {len(URLS)} pages"]

for url in URLS:
    report_lines.append(check_page_grammar(url, tool))

final_report = "\n".join(report_lines)
print(final_report)

# 🚀 Send to Slack if webhook is configured
if SLACK_WEBHOOK_URL:
    slack_payload = {"text": final_report[:3500]}  # Slack limit safeguard
    try:
        slack_response = requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
        if slack_response.status_code == 200:
            print("\n✅ Report sent to Slack.")
        else:
            print(f"\n⚠️ Slack error: {slack_response.status_code} - {slack_response.text}")
    except Exception as slack_error:
        print(f"\n⚠️ Failed to send to Slack: {slack_error}")
else:
    print("\n⚠️ Slack webhook URL not set. Report printed only.")


