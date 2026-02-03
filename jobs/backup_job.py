from datetime import datetime, timezone
from config.logging_config import get_logger
import subprocess

logger = get_logger("backup", "logs/backup.log")

def run_backup():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    logger.info(f"Backup job started for {today}")

    try:
        subprocess.run(
            ["mongodump", "--uri", "YOUR_MONGO_URI"],
            check=True
        )
        logger.info("Backup completed successfully")
    except Exception as e:
        logger.error(f"Backup failed: {e}")


if __name__ == "__main__":
    run_backup()
