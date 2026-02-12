# app/conversation_repo.py

from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import CONVERSATIONS


# ==============================
# CREATE CONVERSATION
# ==============================
async def create_conversation(
    user_hash: str,
    session_id: str,
    platform: str = "LINE",
    language: str = "th"
):

    now = datetime.now(timezone.utc)

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "created_at": now,
        "last_active": now,
        "meta": {
            "platform": platform,
            "language": language
        },
        "messages": []
    }

    result = await db[CONVERSATIONS].insert_one(doc)
    return str(result.inserted_id)


# ==============================
# ADD MESSAGE (embedded)
# ==============================
async def add_message(
    session_id: str,
    role: str,
    text: str,
    sentiment: str | None = None,
    risk_score: float | None = None
):

    now = datetime.now(timezone.utc)

    message_doc = {
        "role": role,            # user / bot
        "text": text,
        "ts": now,
        "sentiment": sentiment,
        "risk_score": risk_score
    }

    await db[CONVERSATIONS].update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": message_doc},
            "$set": {"last_active": now}
        }
    )
