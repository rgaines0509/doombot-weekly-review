# tech_check_v2.py

import os
import socket
import shutil
import platform
import logging

def check_python_version():
    version = platform.python_version()
    logging.info(f"🐍 Python version: {version}")
    if version < "3.8":
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

def run_tech_check():
    logging.info("🚦 Starting tech_check_v2 diagnostic...")

    # Step 1: Python version
    check_python_version()

    # Step 2: Disk space
    check_disk_space()

    # Step 3: Network access
    check_network_connectivity()

    # Step 4: Environment variables (customize this list for your project)
    required_envs = [
        "GOOGLE_API_KEY",   # example
        "WOOCOMMERCE_KEY",
        "WOOCOMMERCE_SECRET"
    ]
    check_env_vars(required_envs)

    logging.info("✅ All tech checks passed successfully.")



