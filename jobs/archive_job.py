# jobs/archive_job.py
from datetime import datetime, timezone, timedelta

from config.logging_config import get_logger
from app.db import db

# -------------------------
# Logger
# -------------------------
logger = get_logger("archive")

# -------------------------
# Config
# -------------------------
ARCHIVE_AFTER_DAYS = 7

# -------------------------
# Helpers
# -------------------------
def utc_now():
    return datetime.now(timezone.utc)

# -------------------------
# Archive Logic
# -------------------------
def run_archive():
    logger.info("Archive job started")

    cutoff_ts = utc_now() - timedelta(days=ARCHIVE_AFTER_DAYS)

    result = db.messages.update_many(
        {
            "ts": {"$lt": cutoff_ts},
            "_archived_at": None
        },
        {
            "$set": {"_archived_at": utc_now()}
        }
    )

    logger.info(
        f"Archive job completed | archived={result.modified_count}"
    )

# -------------------------
# Entry point
# -------------------------
if __name__ == "__main__":
    run_archive()
