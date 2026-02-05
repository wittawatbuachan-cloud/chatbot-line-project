# app/incident_repo.py
from datetime import datetime, timezone
from config.db import db
from app.collections import INCIDENTS

async def create_incident(
    conversation_id: str,
    user_hash: str,
    risk_score: float,
    keywords: list[str]
):
    doc = {
        "conversation_id": conversation_id,
        "user_hash": user_hash,
        "risk_score": float(risk_score),
        "keywords": keywords,
        "status": "open",
        "created_at": datetime.now(timezone.utc),
        "handled_at": None,
        "note": ""
    }
    result = await db[INCIDENTS].insert_one(doc)
    return str(result.inserted_id)
