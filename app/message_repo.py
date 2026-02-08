# app/message_repo.py
from datetime import datetime
from typing import List, Optional
from config.db import get_db
from config.logging_config import get_logger

logger = get_logger("message_repo", "logs/message.log")

def utc_now():
    return datetime.utcnow()

async def insert_message(
    *,
    user_hash: str,
    session_id: str,
    role: str,
    content: str,
    intent: Optional[str] = None,
    emotion_score: Optional[float] = None,
    risk_level: int = 0,
    risk_keywords: Optional[List[str]] = None,
    source: str = "line"
):
    """
    Insert a message document with optional analysis fields.
    """
    db = get_db()

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "role": role,
        "content": content,
        "intent": intent,
        "emotion_score": emotion_score,
        "risk_level": int(risk_level) if risk_level is not None else 0,
        "risk_keywords": risk_keywords or [],
        "source": source,
        "created_at": utc_now(),
        "archived_at": None,
        "handled": False
    }

    await db.messages.insert_one(doc)
    logger.info(f"💾 Insert message role={role} session={session_id} risk={doc['risk_level']}")
    return doc
