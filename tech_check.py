# 🛠️ tech_check.py — Basic Technical Audit
import requests

PAGES = [
    "https://quickbookstraining.com/",
    "https://quickbookstraining.com/quickbooks-courses",
    "https://quickbookstraining.com/plans-and-pricing",
    "https://quickbookstraining.com/learn-quickbooks",
    "https://quickbookstraining.com/live-quickbooks-help",
    "https://quickbookstraining.com/quickbooks-classes",
    "https://quickbookstraining.com/about-us",
    "https://quickbookstraining.com/contact-us",
    "https://quickbookstraining.com/quickbooks-certification",
    "https://quickbookstraining.com/quickbooks-online-certification"
    "https://quickbookstraining.com/quickbooks-desktop-certification",
    "https://quickbookstraining.com/quickbooks-bookkeeping-certification"
    "https://quickbookstraining.com/quickbooks-certification-online",
    "https://quickbookstraining.com/quickbooks-certification-exam"
    "https://quickbookstraining.com/terms-and-conditions",
    "https://quickbookstraining.com/privacy-policy"
]

def run_tech_check():
    print("🛠️ TECH CHECK RESULTS\n========================")
    for url in PAGES:
        try:
            response = requests.get(url, timeout=10)
            status = response.status_code
            if status == 200:
                print(f"✅ {url} is reachable.")
            else:
                print(f"⚠️ {url} responded with status code {status}.")
        except Exception as e:
            print(f"❌ {url} could not be reached: {e}")

if __name__ == "__main__":
    run_tech_check()

