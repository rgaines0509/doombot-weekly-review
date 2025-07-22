# tech_check_v2.py
import os, socket, shutil, platform, logging, subprocess, sys, textwrap
import requests
from bs4 import BeautifulSoup

# ---------- Tech checks ----------
def check_python_version():
    ver = platform.python_version()
    logging.info(f"🐍 Python {ver}")
    if tuple(map(int, ver.split("."))) < (3, 8):
        raise EnvironmentError("Python 3.8+ required")

def check_disk():
    free_gb = shutil.disk_usage("/").free // 2**30
    logging.info(f"💾 Free disk: {free_gb} GB")
    if free_gb < 2:
        raise OSError("Less than 2 GB free")

def check_network(host="8.8.8.8", port=53):
    try:
        socket.create_connection((host, port), timeout=3)
        logging.info("🌐 Network OK")
    except Exception:
        raise ConnectionError("No outbound network")

def check_env(required):
    missing = [v for v in required if os.getenv(v) is None]
    if missing:
        raise EnvironmentError(f"Missing env vars: {', '.join(missing)}")
    logging.info("🔐 Env vars present")

# ---------- Lightweight grammar check ----------
def ensure_language_tool():
    """
    language_tool_python pulls a 200 MB JAR the first time.
    We import lazily so other parts can still run if it fails.
    """
    try:
        import language_tool_python  # noqa: F401
    except ImportError:
        logging.info("📦 Installing language-tool-python on the fly…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "language_tool_python"])
        import language_tool_python  # type: ignore

def grammar_issues(text, limit=10):
    ensure_language_tool()
    import language_tool_python  # type: ignore
    tool = language_tool_python.LanguageTool("en-US")
    matches = tool.check(text)
    issues = []
    for m in matches[:limit]:
        context = m.context.strip()
        sug = ", ".join(m.replacements[:3]) or "—"
        issues.append(f"• {m.ruleId}: “{context}” → {sug}")
    return issues

# ---------- Website scanner ----------
def fetch_text(url):
    try:
        html = requests.get(url, timeout=15).text
    except Exception as e:
        return "", f"⚠️ {url} — fetch error: {e}"
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)[:20000], ""

def run_site_report(urls):
    logging.info("📝 Starting website grammar scan…")
    report_lines = []
    for url in urls:
        txt, err = fetch_text(url)
        if err:
            report_lines.append(err)
            continue
        issues = grammar_issues(txt)
        if issues:
            report_lines.append(f"\n🔎 Issues on {url}:")
            report_lines.extend(issues)
        else:
            report_lines.append(f"✅ {url} — no issues found")
    log_block = "\n".join(report_lines) or "✅ No issues on any page"
    logging.info("\n" + textwrap.dedent(f"""
        ===============================
        📝 WEBSITE GRAMMAR REPORT
        ===============================
        {log_block}
        ===============================
    """).strip())

# ---------- Master runner ----------
def run_tech_check():
    logging.info("🚦 tech_check_v2 starting…")
    # System checks
    check_python_version()
    check_disk()
    check_network()
    check_env(["GOOGLE_API_KEY", "WOOCOMMERCE_KEY", "WOOCOMMERCE_SECRET"])
    logging.info("✅ System tech checks passed")

    # Website report
    urls = [
        "https://quickbookstraining.com",
        "https://quickbookstraining.com/classes",
        "https://quickbookstraining.com/contact",
    ]
    run_site_report(urls)

