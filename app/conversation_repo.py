# app/conversation_repo.py
from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import CONVERSATIONS

async def create_conversation(user_hash: str, channel: str = "LINE"):
    doc = {
        "user_hash": user_hash,
        "channel": channel,
        "started_at": datetime.now(timezone.utc),
        "ended_at": None,
        "status": "active"
    }
    result = await db[CONVERSATIONS].insert_one(doc)
    return str(result.inserted_id)
