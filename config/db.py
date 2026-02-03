import motor.motor_asyncio
from datetime import datetime, timezone
from app.config import settings
from config.logging_config import get_logger

logger = get_logger("db", "logs/app.log")

client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.mongo_uri,
    serverSelectionTimeoutMS=3000
)

db = client[settings.mongo_db]

MESSAGES_COL = "messages"
INCIDENTS_COL = "incidents"


async def check_db_connection():
    try:
        await client.admin.command("ping")
        logger.info("MongoDB connection OK")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False


async def insert_conversation(user_hash: str, session_id: str, message: dict):
    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "message": message,
        "ts": datetime.now(timezone.utc)
    }
    res = await db[MESSAGES_COL].insert_one(doc)
    logger.info(f"Inserted conversation: {res.inserted_id}")
    return str(res.inserted_id)


async def append_conversation_session(
    user_hash: str,
    session_id: str,
    role: str,
    text: str,
    sentiment=None,
    risk_score: float = 0.0
):
    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "role": role,
        "text": text,
        "sentiment": sentiment,
        "risk_score": float(risk_score),
        "ts": datetime.now(timezone.utc),
        "processed": True
    }
    res = await db[MESSAGES_COL].insert_one(doc)
    logger.info(f"Message stored: {res.inserted_id}")
    return str(res.inserted_id)


async def create_incident(
    user_hash: str,
    session_id: str,
    risk_score: float,
    keywords: list
):
    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "trigger_ts": datetime.now(timezone.utc),
        "risk_score": float(risk_score),
        "keywords": keywords,
        "notified_user": True,
        "notified_admin": True,
        "notified_ts": datetime.now(timezone.utc),
        "status": "open",
        "handled_by": None,
        "notes": ""
    }
    res = await db[INCIDENTS_COL].insert_one(doc)
    logger.warning(f"Incident created: {res.inserted_id}")
    return str(res.inserted_id)
