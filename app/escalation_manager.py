# app/escalation_manager.py

from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import INCIDENTS
from app.audit_repo import record_audit


async def create_incident(
    user_hash: str,
    session_id: str,
    emotion: str,
    risk_score: float,
    keywords: list[str],
    content: str
):
    """
    สร้าง incident เมื่อ risk สูง
    """

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "emotion": emotion,
        "risk_score": risk_score,
        "keywords": keywords,
        "content": content,
        "status": "open",
        "trigger_ts": datetime.now(timezone.utc)
    }

    result = await db[INCIDENTS].insert_one(doc)
    incident_id = str(result.inserted_id)

    # ✅ บันทึก audit (system action)
    await record_audit(
        action="create_incident",
        actor="system",
        detail={
            "incident_id": incident_id,
            "risk_score": risk_score
        },
        target_type="incident",
        target_id=incident_id
    )

    return incident_id


async def create_incident(
    user_hash: str,
    session_id: str,
    emotion: str,
    risk_level: str,
    keywords: list,
    content: str
):
    from config.db import get_db
    from datetime import datetime
    from app.audit_repo import record_audit

    db = get_db()

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "emotion": emotion,
        "risk_level": risk_level,
        "keywords": keywords,
        "content": content,
        "status": "open",
        "created_at": datetime.utcnow()
    }

    result = await db.incidents.insert_one(doc)

    # บันทึก audit log
    await record_audit(
        actor="system",
        action="create_incident",
        target_type="incident",
        target_id=str(result.inserted_id),
        detail={
            "user_hash": user_hash,
            "risk_level": risk_level
        }
    )

    return str(result.inserted_id)