# main.py
import logging
from tech_check_v2 import run_tech_check

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True  # overwrite GH Actions default formatter
)

def main():
    logging.info("🚀 Doombot weekly run start")
    try:
        run_tech_check()
        logging.info("🏁 Doombot run finished (success)")
    except Exception as e:
        logging.exception(f"🔥 Doombot failed: {e}")
        raise  # fail the workflow loudly

if __name__ == "__main__":
    main()











