# 🛠️ Doombot Tech Check Script (Enhanced with Debugging)
import httpx
import time

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
    "https://quickbookstraining.com/quickbooks-online-certification",
    "https://quickbookstraining.com/quickbooks-desktop-certification",
    "https://quickbookstraining.com/quickbooks-bookkeeping-certification",
    "https://quickbookstraining.com/quickbooks-certification-online",
    "https://quickbookstraining.com/quickbooks-certification-exam",
    "https://quickbookstraining.com/terms-and-conditions",
    "https://quickbookstraining.com/privacy-policy"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

def run_tech_check():
    print("🛠️ DOOMBOT TECH CHECK RESULTS\n==============================")
    with httpx.Client(http2=True, headers=HEADERS, timeout=10, follow_redirects=True) as client:
        for url in PAGES:
            try:
                start = time.time()
                res = client.get(url)
                duration = round(time.time() - start, 2)

                if res.status_code == 200:
                    print(f"✅ {url} → {res.status_code} OK (final: {res.url}) in {duration}s")
                else:
                    print(f"⚠️ {url} → {res.status_code} (final: {res.url}) in {duration}s")
            except httpx.RequestError as e:
                print(f"❌ {url} could not be reached: {e}")

if __name__ == "__main__":
    run_tech_check()


