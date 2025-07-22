# main.py

import logging
from datetime import datetime
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
        # Step 1: Run technical check
        logging.info("🔍 Running technical check...")
        run_tech_check()
        logging.info("✅ Technical check complete.")

        # Step 2: Placeholder for Google Docs automation
        # logging.info("📄 Updating Google Doc with latest report...")
        # update_google_doc()
        # logging.info("✅ Google Doc updated.")

        # Step 3: Placeholder for Slack preview
        # logging.info("📤 Sending preview to Slack...")
        # send_slack_preview()
        # logging.info("✅ Slack preview sent.")

    except Exception as e:
        logging.error(f"🔥 An error occurred: {e}")
    finally:
        logging.info("🏁 Doombot Weekly Review finished.")

if __name__ == "__main__":
    main()










