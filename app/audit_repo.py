# app/audit_repo.py

from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import AUDIT_LOGS


async def log_action(
    action: str,
    actor: str,
    detail: dict | None = None,
    target_type: str | None = None,
    target_id: str | None = None
):
    """
    บันทึก audit trail
    """

    doc = {
        "action": action,
        "actor": actor,
        "target_type": target_type,
        "target_id": target_id,
        "detail": detail or {},
        "created_at": datetime.now(timezone.utc)
    }

    await db[AUDIT_LOGS].insert_one(doc)
