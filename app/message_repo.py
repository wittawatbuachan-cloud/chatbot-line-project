from typing import List
from config.db import db
from config.logging_config import get_logger
from app.utils.time import utc_now, to_local

logger = get_logger("message_repo", "logs/message.log")

async def insert_message(*, user_hash: str, session_id: str, role: str, content: str, expire_at=None):
    if db is None:
        raise RuntimeError("❌ MongoDB not initialized")

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "role": role,
        "content": content,
        "ts": utc_now(),
        "expireAt": expire_at,
        "_archived_at": None
    }

    await db.messages.insert_one(doc)
    logger.info(f"Insert message session={session_id} role={role}")
