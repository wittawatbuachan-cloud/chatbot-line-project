# jobs/backup_job.py
from datetime import datetime
from typing import Any, Dict, List
from bson import ObjectId
from config.db import get_db
from config.logging_config import get_logger

logger = get_logger("backup_job", "logs/backup.log")


def _serialize(v: Any):
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, list):
        return [_serialize(i) for i in v]
    if isinstance(v, dict):
        return {k: _serialize(val) for k, val in v.items()}
    return v


async def backup_messages_collection(triggered_by: str | None = None) -> Dict:
    db = get_db()
    backup_time = datetime.utcnow()

    meta = {
        "source_collection": "messages",
        "timestamp": backup_time,
        "count": 0,
        "storage": "mongodb",
        "triggered_by": triggered_by,
        "status": "completed"
    }

    meta_res = await db.backups.insert_one(meta)
    backup_id = str(meta_res.inserted_id)

    cursor = db.messages.find({})
    docs_to_insert: List[Dict] = []

    async for doc in cursor:
        doc["original_id"] = str(doc["_id"])
        doc["backup_id"] = backup_id
        doc.pop("_id", None)
        docs_to_insert.append(doc)

    count = 0
    if docs_to_insert:
        await db.messages_backup.insert_many(docs_to_insert)
        count = len(docs_to_insert)

    await db.backups.update_one(
        {"_id": meta_res.inserted_id},
        {"$set": {"count": count}}
    )

    logger.info(
        f"📦 Backup success: messages → messages_backup "
        f"({count} records) backup_id={backup_id}"
    )

    return {
        "backup_id": backup_id,
        "timestamp": backup_time.isoformat(),
        "count": count,
        "storage": "mongodb",
    }


async def get_backup_metadata(limit: int = 100) -> List[Dict]:
    db = get_db()
    docs = await db.backups.find({}).sort("timestamp", -1).to_list(limit)
    return [
        {k: (_serialize(v) if k != "_id" else str(v)) for k, v in d.items()}
        for d in docs
    ]


async def fetch_backup_docs(backup_id: str) -> List[Dict]:
    db = get_db()
    cursor = db.messages_backup.find({"backup_id": backup_id})
    docs = []
    async for doc in cursor:
        docs.append({k: _serialize(v) for k, v in doc.items()})
    return docs
