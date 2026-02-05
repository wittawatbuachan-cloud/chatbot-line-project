# app/message_repo.py
from typing import List
from datetime import datetime
from config.db import db
from config.logging_config import get_logger

logger = get_logger("message_repo", "logs/message.log")

def utc_now():
    return datetime.utcnow()

async def insert_message(*, user_hash: str, session_id: str, role: str, content: str):
    if db is None:
        raise RuntimeError("❌ MongoDB not connected (db is None)")

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "role": role,
        "content": content,
        "ts": utc_now(),
        "_archived_at": None
    }

    await db.messages.insert_one(doc)
    logger.info(f"💾 Insert message role={role} session={session_id}")
