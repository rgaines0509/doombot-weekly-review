# main.py

import logging
from tech_check_fresh import run_tech_check

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    logging.info("🚀 Doombot Weekly Website Review starting...")

    try:
        logging.info("🔍 Running technical check (from tech_check_fresh.py)...")
        run_tech_check()
        logging.info("✅ Technical check completed.")
    except Exception as e:
        logging.error(f"❌ Tech check failed: {e}")
    finally:
        logging.info("🏁 Doombot Weekly Review finished.")

if __name__ == "__main__":
    main()













