import os
import json
import asyncio
import logging
from doomsite_check import run_check
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

GOOGLE_DOC_TITLE = "Doombot Weekly Website Review"

def authenticate_docs_api():
    key_path = "service_account_key.json"
    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/documents"]
    )
    return build('docs', 'v1', credentials=credentials)

def get_or_create_doc(service, title):
    docs = service.documents()
    # Try to find the document by title (optional, could be cached)
    body = {"title": title}
    doc = docs.create(body=body).execute()
    return doc['documentId']

def write_to_google_doc(service, doc_id, content_lines):
    requests = []
    # Clear existing content first
    requests.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": 1_000_000}}})

    # Add the new content
    for line in content_lines:
        requests.append({
            "insertText": {
                "location": {"index": 1},
                "text": line + "\n"
            }
        })

    service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

async def main():
    logger.info("🚀 Doombot Report Starting...")
    results = await run_check(URLS_TO_CHECK)

    # Format the report
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_lines = [f"# Doombot Weekly Website Review", f"Generated: {now}", ""]
    for result in results:
        report_lines.append(f"## {result['url']}")
        report_lines.extend(result['report'])
        report_lines.append("")

    # Save to Google Docs
    logger.info("📄 Authenticating and writing report to Google Docs...")
    service = authenticate_docs_api()
    doc_id = get_or_create_doc(service, GOOGLE_DOC_TITLE)
    write_to_google_doc(service, doc_id, report_lines)

    logger.info("✅ Google Doc updated successfully.")

if __name__ == "__main__":
    asyncio.run(main())



