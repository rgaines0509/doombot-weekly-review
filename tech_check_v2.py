# tech_check_v2.py

import os
import socket
import shutil
import platform
import logging
import requests
from bs4 import BeautifulSoup
import language_tool_python

# ---------- System Tech Checks ----------

def check_python_version():
    version = platform.python_version()
    logging.info(f"🐍 Python version: {version}")
    if tuple(map(int, version.split("."))) < (3, 8):
        raise EnvironmentError("Python 3.8+ is required.")

def check_disk_space():
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    logging.info(f"💾 Disk space free: {free_gb} GB")
    if free_gb < 2:
        raise OSError("Not enough disk space (less than 2 GB free).")

def check_network_connectivity(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        logging.info("🌐 Network connectivity: OK")
    except Exception:
        raise ConnectionError("Unable to reach the internet (8.8.8.8)")

def check_env_vars(required_vars):
    missing = [var for var in required_vars if os.getenv(var) is None]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")
    logging.info("🔐 Environment variables: OK")

# ---------- Website Grammar/Spelling Review ----------

def crawl_pages_and_check_grammar(urls):
    tool = language_tool_python.LanguageTool('en-US')
    results = []

    for url in urls:
        try:
            logging.info(f"🌐 Checking: {url}")
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            matches = tool.check(text)

            if matches:
                results.append(f"\n🔎 Issues found on {url}:")
                for match in matches[:10]:  # Limit to first 10 issues per page
                    context = match.context.replace("\n", " ").strip()
                    suggestion = ", ".join(match.replacements[:3]) or "—"
                    results.append(f"• {match.ruleId}: “{context}” → {suggestion}")
            else:
                results.append(f"\n✅ No issues found on {url}")

        except Exception as e:
            results.append(f"\n⚠️ Error checking {url}: {e}")

    return results

# ---------- Master Runner ----------

def run_tech_check():
    logging.info("🚦 Starting tech_check_v2 diagnostic...")

    # 1. System checks
    check_python_version()
    check_disk_space()
    check_network_connectivity()
    check_env_vars([])  # You can add env var names here if needed

    logging.info("✅ System checks passed.\n")

    # 2. Website grammar/spelling checks
    urls_to_check = [
        "https://quickbookstraining.com",
        "https://quickbookstraining.com/classes",
        "https://quickbookstraining.com/contact",
        "https://quickbookstraining.com/about",
        "https://quickbookstraining.com/instructors",
        "https://quickbookstraining.com/faqs",
        "https://quickbookstraining.com/privacy-policy",
        "https://quickbookstraining.com/terms-of-service",
        "https://quickbookstraining.com/free-resources",
        "https://quickbookstraining.com/quickbooks-certification-training"
    ]

    logging.info("📝 Starting full website grammar review...")
    report = crawl_pages_and_check_grammar(urls_to_check)

    logging.info("\n" + "=" * 40)
    logging.info("📝 WEBSITE GRAMMAR REPORT")
    logging.info("=" * 40)
    for line in report:
        logging.info(line)
    logging.info("=" * 40 + "\n")



