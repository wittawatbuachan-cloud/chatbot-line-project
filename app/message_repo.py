# app/message_repo.py
from config.db import get_db
from datetime import datetime
from config.logging_config import get_logger

logger = get_logger("message_repo", "logs/message_repo.log")


async def insert_message(
    *,
    user_hash: str,
    session_id: str,
    role: str,
    content: str,
    emotion: str | None = None,
    risk_level: str | None = None,
    source: str = "system"
):

    db = get_db()

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "role": role,
        "content": content,
        "emotion": emotion,
        "risk_level": risk_level,
        "source": source,
        "created_at": datetime.utcnow()
    }

    await db.messages.insert_one(doc)

    logger.info(
        f"💾 Insert message role={role} session={session_id} risk={risk_level}"
    )
