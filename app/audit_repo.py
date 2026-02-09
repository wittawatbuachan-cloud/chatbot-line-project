# app/audit_repo.py
from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import AUDIT_LOGS

async def log_action(
    action: str,
    actor: str,
    detail: dict | None = None
):
    doc = {
        "action": action,
        "actor": actor,
        "detail": detail or {},
        "timestamp": datetime.now(timezone.utc)
    }
    await db[AUDIT_LOGS].insert_one(doc)
