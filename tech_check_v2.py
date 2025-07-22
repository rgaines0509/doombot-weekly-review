# tech_check_v2.py

import os
import socket
import shutil
import platform
import logging
import requests
from bs4 import BeautifulSoup
import language_tool_python

# ---------- TECH CHECKS ----------

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
    logging.info("🔐 Environment variables check: OK")

# ---------- WEBSITE GRAMMAR CHECK ----------

def fetch_text_from_url(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Remove nav, script, style, footer
        for tag in soup(["nav", "script", "style", "footer"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return text[:20000]  # limit to avoid overload
    except Exception as e:
        logging.warning(f"⚠️ Failed to fetch {url}: {e}")
        return ""

def run_website_grammar_report(urls):
    tool = language_tool_python.LanguageTool('en-US')
    full_report = []

    for url in urls:
        logging.info(f"🔎 Scanning {url}")
        text = fetch_text_from_url(url)
        if not text:
            continue

        matches = tool.check(text)
        if matches:
            report_lines = [f"• {m.ruleId} at '{m.context.strip()}' — Suggestion: {m.replacements}" for m in matches[:10]]
            full_report.append(f"\n🔍 Issues found on {url}:\n" + "\n".join(report_lines))
        else:
            full_report.append(f"\n✅ No issues found on {url}")

    print("\n📝 Website Grammar Report")
    print("----------------------------")
    print("\n".join(full_report))
    print("\n✔️ Grammar check complete.")

# ---------- MASTER RUNNER ----------

def run_tech_check():
    logging.info("🚦 Starting tech_check_v2 diagnostic...")

    check_python_version()
    check_disk_space()
    check_network_connectivity()

    required_envs = [
        "GOOGLE_API_KEY",     # Replace with actual env vars if needed
        "WOOCOMMERCE_KEY",
        "WOOCOMMERCE_SECRET"
    ]
    check_env_vars(required_envs)

    logging.info("✅ All tech checks passed successfully.")

    # Run the grammar/spelling review for your site
    urls_to_check = [
        "https://quickbookstraining.com",  # Replace or expand as needed
        "https://quickbookstraining.com/classes",
        "https://quickbookstraining.com/contact"
    ]
    run_website_grammar_report(urls_to_check)

