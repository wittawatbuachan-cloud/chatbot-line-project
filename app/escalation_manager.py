# app/escalation_manager.py

from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import INCIDENTS
from app.audit_repo import log_action


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
    await log_action(
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
