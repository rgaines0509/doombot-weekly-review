import os
import requests
from bs4 import BeautifulSoup
import language_tool_python

# ✅ URLs to check
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

# 🎯 Tags to scan for text blocks
TEXT_TAGS = ['p', 'li', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'td']

# 🧪 Grammar checker
tool = language_tool_python.LanguageTool('en-US')

# 📤 Slack webhook
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def check_page_grammar_by_block(url, tool):
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Doombot/2.0'})
        soup = BeautifulSoup(response.text, 'lxml')
        elements = soup.find_all(TEXT_TAGS)
        report_lines = [f"\n🔍 {url}"]

        issue_count = 0

        for elem in elements:
            text = elem.get_text(strip=True)
            if not text or len(text) < 30:  # Skip short or empty strings
                continue

            matches = tool.check(text)

            for match in matches[:3]:  # Limit per element for brevity
                tag = elem.name
                identifier = elem.get('id') or elem.get('class') or 'no-id/class'
                snippet = text[:80] + '...' if len(text) > 80 else text

                report_lines.append(
                    f"- Issue in <{tag} id/class={identifier}>: \"{snippet}\"\n  ➤ {match.message} | Suggest: {match.replacements[:2]}"
                )
                issue_count += 1

        if issue_count == 0:
            report_lines.append("- No issues found 🎉")

        return "\n".join(report_lines)

    except Exception as e:
        return f"\n🔍 {url}\n- Error: {e}"

# 🧾 Compile full report
final_results = ["🕵️ Doombot Website Grammar Check with Location Context"]
for url in URLS:
    final_results.append(check_page_grammar_by_block(url, tool))

final_report = "\n".join(final_results)
print(final_report)

# 📢 Send to Slack
if SLACK_WEBHOOK_URL:
    slack_payload = {"text": final_report[:3500]}  # Truncate to stay Slack-safe
    try:
        slack_response = requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
        if slack_response.status_code == 200:
            print("\n✅ Report sent to Slack.")
        else:
            print(f"\n⚠️ Slack error: {slack_response.status_code} - {slack_response.text}")
    except Exception as slack_error:
        print(f"\n⚠️ Failed to send to Slack: {slack_error}")
else:
    print("\n⚠️ Slack webhook not set. Report printed only.")




