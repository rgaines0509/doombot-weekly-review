# tech_check_v2.py

import os
import socket
import shutil
import platform
import logging

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
    logging.info("🔐 Environmen
