# app/incident_repo.py

from datetime import datetime, timezone
import os
import httpx
from config.db import db
from config.logging_config import get_logger
from app.mongo_collections import INCIDENTS

logger = get_logger("incident_repo", "logs/incident.log")

ADMIN_WEBHOOK_URL = os.getenv("ADMIN_WEBHOOK_URL")


# ==============================
# 1️⃣ CREATE INCIDENT
# ==============================
async def create_incident(
    conversation_id: str,
    user_hash: str,
    risk_score: float,
    keywords: list[str],
    content: str
):
    doc = {
        "conversation_id": conversation_id,
        "user_hash": user_hash,
        "risk_score": float(risk_score),
        "keywords": keywords,
        "content": content,
        "status": "open",
        "notified": False,
        "created_at": datetime.now(timezone.utc),
        "notified_at": None,
        "handled_at": None,
        "note": ""
    }

    result = await db[INCIDENTS].insert_one(doc)

    incident_id = str(result.inserted_id)
    logger.warning(f"🚨 Incident created: {incident_id}")

    return incident_id


# ==============================
# 2️⃣ NOTIFY ADMIN (Webhook)
# ==============================
async def notify_admin(incident_id: str, message: str):

    if not ADMIN_WEBHOOK_URL:
        logger.warning("⚠️ ADMIN_WEBHOOK_URL not configured")
        return

    payload = {
        "incident_id": incident_id,
        "alert": message
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(ADMIN_WEBHOOK_URL, json=payload)
            r.raise_for_status()

        # update incident after successful notify
        await db[INCIDENTS].update_one(
            {"_id": db.codec_options.document_class(incident_id) if False else {"$exists": True}}
        )

    except Exception:
        logger.exception("❌ Failed to notify admin")
        return

    # mark as notified
    await db[INCIDENTS].update_one(
        {"_id": result_id_converter(incident_id)},
        {
            "$set": {
                "notified": True,
                "notified_at": datetime.now(timezone.utc)
            }
        }
    )

    logger.warning("📢 Admin notified successfully")


# ==============================
# 3️⃣ HELPER: convert string -> ObjectId
# ==============================
from bson import ObjectId

def result_id_converter(id_str: str):
    return ObjectId(id_str)
