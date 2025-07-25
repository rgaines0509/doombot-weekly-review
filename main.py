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
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
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
        doc_id = doc.get('documentId')
        print(f"🆕 Created new doc: {doc.get('title')} (ID: {doc_id})")

        # Share with Ron's email
        drive_service.permissions().create(
            fileId=doc_id,
            body={
                'type': 'user',
                'role': 'writer',
                'emailAddress': 'rgaines@quickbookstraining.com'
            },
            fields='id'
        ).execute()
        print(f"📬 Shared doc with rgaines@quickbookstraining.com")

        return doc_id

def write_report_to_google_doc(report, document_id, service):
    body = {
        'requests': [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': report
                }
            }
        ]
    }
    service.documents().batchUpdate(documentId=document_id, body=body).execute()

async def main():
    print("🚀 Doombot Report Starting...")
    results = await run_check(URLS_TO_CHECK)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_report = f"Doombot Weekly Report - {timestamp}\n\n" + "\n".join(results)

    # Write to local Markdown backup
    with open("weekly_report.md", "w", encoding="utf-8") as f:
        f.write(full_report)

    # Write to Google Doc
    creds = get_service_account_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    doc_id = find_or_create_doc(docs_service, DOC_TITLE)
    write_report_to_google_doc(full_report, doc_id, docs_service)

    print("✅ Doombot report complete.")
    print(f"📄 View it here: https://docs.google.com/document/d/{doc_id}/edit")

if __name__ == "__main__":
    asyncio.run(main())









