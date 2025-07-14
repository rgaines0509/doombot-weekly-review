# 📘 Doombot Grammar & Continuity Review Script
# Enhanced with location-level context and formatting for Slack

import os
import requests
from language_tool_python import LanguageTool

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

PAGES = {
    "https://quickbookstraining.com/": "Home page content here...",
    "https://quickbookstraining.com/quickbooks-courses": "Courses page content here...",
    "https://quickbookstraining.com/plans-and-pricing": "Pricing page content here..."
    # Add more pages and HTML/text content here
}

def get_surrounding_text(text, error_offset, length, radius=40):
    start = max(0, error_offset - radius)
    end = min(len(text), error_offset + length + radius)
    return text[start:end].replace("\n", " ").strip()

def run_grammar_checks():
    tool = LanguageTool('en-US')
    final_results = ["\U0001f4dd *Doombot Grammar Report*\n"]

    for url, content in PAGES.items():
        matches = tool.check(content)
        if not matches:
            final_results.append(f"✅ {url} - No grammar or spelling issues found.")
            continue

        final_results.append(f"🔎 {url}")
        for match in matches:
            issue_type = match.ruleIssueType.capitalize()
            error_text = content[match.offset:match.offset + match.errorLength]
            suggestion = match.replacements[0] if match.replacements else "(no suggestion)"
            context = get_surrounding_text(content, match.offset, match.errorLength)
            highlighted = context.replace(error_text, f"*{error_text}*")
            final_results.append(f"❌ {issue_type}: “{error_text}” ➝ Suggested: “{suggestion}”\n🧠 Context: “…{highlighted}…”")

    report = "\n\n".join(final_results)
    print(report)

    with open("grammar_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    if SLACK_WEBHOOK_URL:
        try:
            slack_payload = {"text": report[:3500]}
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




