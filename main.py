# main.py

import logging
from tech_check_v2 import run_tech_check

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    logging.info("🚀 Doombot Weekly Website Review starting...")

    try:
        logging.info("🔍 Running technical check...")
        run_tech_check()
        logging.info("✅ Technical check completed.")
    except Exception as e:
        logging.error(f"❌ Doombot tech check failed: {e}")
    finally:
        logging.info("🏁 Doombot Weekly Review finished.")

if __name__ == "__main__":
    main()











