from datetime import datetime, timedelta, timezone
from config.logging_config import get_logger

logger = get_logger("session", "logs/app.log")

SESSION_TIMEOUT_MINUTES = 30


def utc_now():
    return datetime.now(timezone.utc)


def start_session(db, user_hash: str):
    now = utc_now()

    doc = {
        "user_hash": user_hash,
        "started_at": now,
        "last_active_at": now,
        "closed_at": None,
        "status": "active",
    }

    res = db.sessions.insert_one(doc)
    logger.info(f"Session started user={user_hash}")
    return res.inserted_id


def touch_session(db, session_id):
    db.sessions.update_one(
        {"_id": session_id, "status": "active"},
        {"$set": {"last_active_at": utc_now()}}
    )


def close_session(db, session_id, reason: str = "timeout"):
    now = utc_now()

    db.sessions.update_one(
        {"_id": session_id, "status": "active"},
        {
            "$set": {
                "status": "closed",
                "closed_at": now,
                "close_reason": reason,
            }
        }
    )

    logger.warning(f"Session closed id={session_id} reason={reason}")


def get_or_create_session(db, user_hash: str):
    now = utc_now()
    timeout_at = now - timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    session = db.sessions.find_one(
        {"user_hash": user_hash, "status": "active"},
        sort=[("last_active_at", -1)],
    )

    if session:
        if session["last_active_at"] < timeout_at:
            close_session(db, session["_id"], "timeout")
        else:
            touch_session(db, session["_id"])
            return session["_id"]

    return start_session(db, user_hash)


def auto_close_expired_sessions(db) -> int:
    now = utc_now()
    timeout_at = now - timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    res = db.sessions.update_many(
        {
            "status": "active",
            "last_active_at": {"$lt": timeout_at},
        },
        {
            "$set": {
                "status": "closed",
                "closed_at": now,
                "close_reason": "timeout",
            }
        }
    )

    if res.modified_count:
        logger.warning(f"Auto-closed {res.modified_count} sessions")

    return res.modified_count
