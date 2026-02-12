# app/message_repo.py
from config.db import get_db
from datetime import datetime
from config.logging_config import get_logger

logger = get_logger("message_repo", "logs/message_repo.log")


async def insert_message(
    *,
    session_id: str,
    user_hash: str,
    content: str,
    risk_score: float = 0.0,
    keywords: list[str] | None = None
):

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "trigger_ts": datetime.now(timezone.utc),
        "risk_score": risk_score,
        "keywords": keywords or [],
        "notified_user": False,
        "notified_admin": False,
        "notified_ts": None,
        "status": "open",
        "handled_by": None,
        "notes": "",
        "content": content
    }

    await db.messages.insert_one(doc)

    logger.info(
        f"💾 Insert message role={role} session={session_id} risk={risk_level}"
    )
