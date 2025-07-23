import asyncio
import os
from datetime import datetime
from doomsite_check import run_check
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import json

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

DOC_TITLE = "Doombot Weekly Website Review"
SCOPES = ['https://www.googleapis.com/auth/documents']
GOOGLE_DOC_MIME = 'application/vnd.google-apps.document'


def get_service_account_credentials():
    service_account_info = os.environ['GOOGLE_SERVICE_ACCOUNT_KEY']
    service_account_json = json.loads(service_account_info)
    return service_account.Credentials.from_service_account_info(
        service_account_json,
        scopes=SCOPES
    )


def find_or_create_doc(service, title):
    drive_service = build('drive', 'v3', credentials=service._credentials)
    results = drive_service.files().list(
        q=f"name='{title}' and mimeType='{GOOGLE_DOC_MIME}' and trashed = false",
        spaces='drive',
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])

    if items:
        print(f"📄 Found existing doc: {items[0]['name']} (ID: {items[0]['id']})")
        return items[0]['id']
    else:
        body = {'title': title}
        doc = service.documents().create(body=body).execute()
        print(f"🆕 Created new doc: {doc.get('title')} (ID: {doc.get('documentId')})")
        return doc.get('documentId')


def write_report_to_google_doc(report, document_id, service):
    body = {
        'requests': [{
            'insertText': {
                'location': {'index': 1},
                'text': report
            }
        }]
    }
    service.documents().batchUpdate(documentId=document_id, body=body).execute()


def send_report_to_slack(doc_id):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
    slack_message = {
        "text": f"📝 Doombot Weekly Website Review is complete!\n{doc_link}"
    }
    response = requests.post(webhook_url, json=slack_message)
    if response.status_code != 200:
        print("Slack webhook failed:", response.text)
    else:
        print("📤 Sent report to Slack!")


async def main():
    print("🚀 Doombot Report Starting...")
    results = await run_check(URLS_TO_CHECK)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_report = f"Doombot Weekly Report - {timestamp}\n\n"
    for result in results:
        full_report += result + "\n\n"

    print("📝 Connecting to Google Docs API...")
    creds = get_service_account_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    doc_id = find_or_create_doc(docs_service, DOC_TITLE)

    print("📊 Writing report to Google Doc...")
    write_report_to_google_doc(full_report, doc_id, docs_service)

    print("📣 Notifying Slack...")
    send_report_to_slack(doc_id)

    print("✅ Doombot report complete.")


if __name__ == "__main__":
    asyncio.run(main())




