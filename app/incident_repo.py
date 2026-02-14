# app/incident_repo.py

from datetime import datetime, timezone
import os
import httpx
from bson import ObjectId
from config.db import db, get_db
from config.logging_config import get_logger
from app.mongo_collections import INCIDENTS

logger = get_logger("incident_repo", "logs/incident.log")
ADMIN_WEBHOOK_URL = os.getenv("ADMIN_WEBHOOK_URL")


# ==============================
# CREATE INCIDENT
# ==============================
async def create_incident(
    session_id: str,
    user_hash: str,
    risk_score: float,
    keywords: list[str]
):
    
    db = get_db()

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "trigger_ts": datetime.now(timezone.utc),
        "risk_score": float(risk_score),
        "keywords": keywords,
        "notified_user": False,
        "notified_admin": False,
        "notified_ts": None,
        "status": "open",  # open / in_progress / closed
        "handled_by": None,
        "notes": ""
    }

    result = await db[INCIDENTS].insert_one(doc)
    return str(result.inserted_id)


# ==============================
# NOTIFY ADMIN
# ==============================
async def notify_admin(incident_id: str):

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                ADMIN_WEBHOOK_URL,
                json={"incident_id": incident_id}
            )
            response.raise_for_status()

        db = get_db()

        await db[INCIDENTS].update_one(
            {"_id": ObjectId(incident_id)},
            {
                "$set": {
                    "notified_admin": True,
                    "notified_ts": datetime.now(timezone.utc)
                }
            }
        )

    except Exception:
        logger.exception("Failed to notify admin")
