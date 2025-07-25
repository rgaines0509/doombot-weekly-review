import asyncio
import os
import json
from datetime import datetime
from doomsite_check import run_check
from google.oauth2 import service_account
from googleapiclient.discovery import build

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
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
]


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
        q=f"name='{title}' and mimeType='application/vnd.google-apps.document' and trashed = false",
        spaces='drive',
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])

    if items:
        print(f"📄 Found existing doc: {items[0]['name']} (ID: {items[0]['id']})")
        return items[0]['id']
    else:
        doc = service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')
        print(f"🆕 Created new doc: {doc.get('title')} (ID: {doc_id})")

        # Share the doc with Ron
        drive_service.permissions().create(
            fileId=doc_id,
            body={
                'type': 'user',
                'role': 'writer',
                'emailAddress': 'rgaines@quickbookstraining.com'
            },
            fields='id'
        ).execute()
        print(f"📧 Shared doc with rgaines@quickbookstraining.com")

        return doc_id


def write_report_to_google_doc(report, document_id, service):
    requests = [
        {
            'deleteContentRange': {
                'range': {
                    'startIndex': 1,
                    'endIndex': 999999
                }
            }
        },
        {
            'insertText': {
                'location': {'index': 1},
                'text': report
            }
        }
    ]
    service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()


def format_report(sections):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"🧾 Doombot Weekly Website Review\nGenerated: {timestamp}\n\n"
    return header + "\n".join(sections)


async def main():
    print("🚀 Doombot Report Starting...")
    results = await run_check(URLS_TO_CHECK)
    markdown = format_report(results)

    print("📄 Connecting to Google Docs...")
    creds = get_service_account_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    doc_id = find_or_create_doc(docs_service, DOC_TITLE)

    print("📝 Writing report to Google Doc...")
    write_report_to_google_doc(markdown, doc_id, docs_service)

    print("✅ Doombot Check Complete. View report:")
    print(f"https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    asyncio.run(main())









