# jobs/backup_job.py
import json
import os
from datetime import datetime
from config.db import get_db   
from config.logging_config import get_logger

logger = get_logger("backup_job", "logs/backup.log")

BACKUP_DIR = "backups"


def _ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)


def serialize(doc: dict):
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc


async def backup_messages_collection():
    db = get_db()   
    _ensure_backup_dir()

    today = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{BACKUP_DIR}/messages_{today}.json"

    cursor = db.messages.find({})
    documents = []

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        documents.append(serialize(doc))

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    logger.info(f"📦 Backup success: {filename} ({len(documents)} records)")

    return {
        "file": filename,
        "count": len(documents),
        "backup_time": datetime.utcnow().isoformat()
    }
