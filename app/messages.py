# app/messages.py
from typing import List
from config.logging_config import get_logger
from app.db import db
from app.utils.time import utc_now, to_local

logger = get_logger("messages", "logs/app.log")

# -------------------------
# Insert message
# -------------------------

async def insert_message(
    *,
    user_hash: str,
    session_id: str,
    role: str,            # system | user | assistant | risk
    content: str,
    expire_at=None
):
    """
    Insert message into messages collection
    """
    now = utc_now()

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "role": role,
        "content": content,

        # time
        "ts": now,
        "expireAt": expire_at,

        # audit
        "_archived_at": None
    }

    await db.messages.insert_one(doc)
    logger.info(f"Message inserted session={session_id} role={role}")

    return doc


# -------------------------
# Timeline (conversation view)
# -------------------------

async def get_timeline(
    *,
    user_hash: str,
    session_id: str,
    limit: int = 100,
    local_timezone: bool = True
) -> List[dict]:
    """
    Return conversation timeline (sorted by time ASC)
    """
    cursor = (
        db.messages
        .find(
            {
                "user_hash": user_hash,
                "session_id": session_id,
                "_archived_at": None
            }
        )
        .sort("ts", 1)
        .limit(limit)
    )

    results = []
    async for doc in cursor:
        ts = doc["ts"]
        if local_timezone:
            ts = to_local(ts)

        results.append({
            "role": doc["role"],
            "content": doc["content"],
            "timestamp": ts.isoformat()
        })

    return results


# -------------------------
# Session-level stats
# -------------------------

async def count_messages(session_id: str) -> int:
    return await db.messages.count_documents(
        {
            "session_id": session_id,
            "_archived_at": None
        }
    )


# -------------------------
# Soft archive
# -------------------------

async def mark_archived(message_ids: List):
    await db.messages.update_many(
        {"_id": {"$in": message_ids}},
        {"$set": {"_archived_at": utc_now()}}
    )
