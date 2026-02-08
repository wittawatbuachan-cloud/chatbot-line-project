# jobs/backup_jobs.py
import json
import os
from datetime import datetime
from config.db import db
from config.logging_config import get_logger

logger = get_logger("backup_job", "logs/backup.log")

BACKUP_DIR = "backups"


def _ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)


async def backup_messages_collection():
    """
    Backup collection: messages
    Output: backups/messages_YYYY-MM-DD.json
    """
    if db is None:
        raise RuntimeError("❌ MongoDB not connected")

    _ensure_backup_dir()

    today = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{BACKUP_DIR}/messages_{today}.json"

    cursor = db.messages.find({})
    documents = []

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])   # แปลง ObjectId
        documents.append(doc)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    logger.info(f"📦 Backup success: {filename} ({len(documents)} records)")

    return {
        "file": filename,
        "total": len(documents),
        "collection": "messages"
    }
