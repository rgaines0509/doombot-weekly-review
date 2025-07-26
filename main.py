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

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("utf-8", "replace").decode("utf-8"))

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
    items =









