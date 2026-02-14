# app/message_repo.py
from datetime import datetime, timezone
from config.logging_config import get_logger
from config.db import get_db

logger = get_logger("message_repo", "logs/message_repo.log")

async def insert_message(
    *,
    session_id: str,
    user_hash: str,
    role: str,
    content: str,
    risk_score: float = 0.0,
    keywords: list[str] | None = None
) -> str:
    """
    Insert a message doc into the `messages` collection.
    Returns inserted_id as str.
    """
    db = get_db()
    now = datetime.now(timezone.utc)

    doc = {
        "user_hash": user_hash,
        "role": role,
        "session_id": session_id,
        "trigger_ts": now,
        "risk_score": float(risk_score),
        "keywords": keywords or [],
        "notified_user": False,
        "notified_admin": False,
        "notified_ts": None,
        "status": "open",
        "handled_by": None,
        "notes": "",
        "content": content
    }

    result = await db.messages.insert_one(doc)
    inserted_id = str(result.inserted_id)

    logger.info(f"💾 Insert message role={role} session={session_id} id={inserted_id} risk={risk_score}")
    return inserted_id