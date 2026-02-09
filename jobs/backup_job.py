# jobs/backup_jobs.py
import json
from datetime import datetime
from typing import Any, Dict, List
from config.db import get_db
from config.logging_config import get_logger
from bson import ObjectId

logger = get_logger("backup_job", "logs/backup.log")


def _serialize_value(v: Any):
    """
    Convert BSON / Python special types to JSON-serializable values.
    """
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, ObjectId):
        return str(v)
    return v


def serialize_doc(doc: Dict) -> Dict:
    out = {}
    for k, v in doc.items():
        out[k] = _serialize_value(v)
    return out


async def backup_messages_collection(triggered_by: str | None = None) -> Dict:
    """
    Copy all documents from `messages` collection into `messages_backup` collection.
    Also create a metadata document in `backups` collection.

    Returns metadata info:
    {
      "backup_id": "<hex id>",
      "filename": "messages_backup_2026-02-09T12:00:00.json",
      "timestamp": "2026-02-09T12:00:00",
      "count": 123,
      "storage": "mongodb"
    }
    """
    db = get_db()
    backup_time = datetime.utcnow()

    # 1) create metadata doc first so we have a backup_id to tag copied docs
    filename = f"messages_backup_{backup_time.isoformat()}.json"
    meta = {
        "filename": filename,
        "timestamp": backup_time,
        "count": 0,
        "storage": "mongodb",
        "triggered_by": triggered_by,
    }

    meta_res = await db.backups.insert_one(meta)
    backup_id = str(meta_res.inserted_id)

    # 2) iterate messages and prepare docs to insert into messages_backup
    cursor = db.messages.find({})
    docs_to_insert: List[Dict] = []

    async for doc in cursor:
        # keep original id and metadata
        original_id = str(doc.get("_id"))
        doc["original_id"] = original_id
        # tag with backup_id
        doc["backup_id"] = backup_id
        # remove _id so Mongo will create a new one for the backup doc
        if "_id" in doc:
            doc.pop("_id")
        docs_to_insert.append(doc)

    count = 0
    if docs_to_insert:
        res = await db.messages_backup.insert_many(docs_to_insert)
        count = len(res.inserted_ids)

    # 3) update metadata with actual count
    await db.backups.update_one({"_id": meta_res.inserted_id}, {"$set": {"count": count}})

    logger.info(f"📦 Backup success: {filename} ({count} records) backup_id={backup_id}")
    print(f"📦 Backup success: {filename} ({len(documents)} records)")

    # 4) return serializable metadata
    return {
        "backup_id": backup_id,
        "filename": filename,
        "timestamp": backup_time.isoformat(),
        "count": count,
        "storage": "mongodb",
    }


async def get_backup_metadata(limit: int = 100) -> List[Dict]:
    db = get_db()
    docs = await db.backups.find({}).sort("timestamp", -1).to_list(length=limit)
    out = []
    for d in docs:
        dd = {k: (_serialize_value(v) if k != "_id" else str(v)) for k, v in d.items()}
        # ensure consistent keys
        if isinstance(dd.get("timestamp"), str):
            pass
        out.append(dd)
    return out


async def fetch_backup_docs(backup_id: str) -> List[Dict]:
    """
    Return list of documents for a given backup_id from messages_backup collection.
    The returned docs are JSON-serializable.
    """
    db = get_db()
    cursor = db.messages_backup.find({"backup_id": backup_id})
    docs = []
    async for doc in cursor:
        # serialize ObjectId and datetime fields
        serialized = {}
        for k, v in doc.items():
            if k == "_id":
                serialized[k] = str(v)
            else:
                serialized[k] = _serialize_value(v)
        docs.append(serialized)
    return docs
