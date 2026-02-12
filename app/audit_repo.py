# app/audit_repo.py

from datetime import datetime, UTC
from config.db import db, get_db
from config.logging_config import get_logger

logger = get_logger("audit_repo", "logs/audit_repo.log")


# ===============================
# CREATE AUDIT LOG
# ===============================
async def record_audit(
    *,
    actor: str,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    detail: dict | None = None
):
    db = get_db()

    doc = {
        "actor": actor,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "detail": detail or {},
        "created_at": datetime.utcnow()
    }

    await db.audit_logs.insert_one(doc)
    logger.info(f"Audit created: {action}")


# ===============================
# GET AUDIT LOGS
# ===============================
async def get_audit_logs(
    filter_q: dict | None = None,
    limit: int = 100
):
    db = get_db()

    query = filter_q or {}

    cursor = (
        db.audit_logs
        .find(query)
        .sort("created_at", -1)
        .limit(limit)
    )

    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)

    return results


async def log_action(
    action: str,
    actor: str,
    detail: dict,
    target_type: str,
    target_id: str
):
    audit_record = {
        "action": action,
        "actor": actor,
        "detail": detail,
        "target_type": target_type,
        "target_id": target_id,
        "timestamp": datetime.now(UTC)
    }

    db.audit_logs.insert_one(audit_record)

    return audit_record