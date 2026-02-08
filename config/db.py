# config/db.py
import motor.motor_asyncio
from app.config import settings
import logging
from typing import Optional

logger = logging.getLogger("db")

client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
db = None


async def connect_db_if_needed():
    """
    Lazy MongoDB connection (Render-safe)
    """
    global client, db

    if db is not None:
        return db

    logger.info("🔌 Lazy connecting to MongoDB...")

    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongo_uri,
            serverSelectionTimeoutMS=3000,
        )

        # ❗ ไม่มี ping
        db = client[settings.mongo_db]

        logger.info("✅ MongoDB client ready")
        return db

    except Exception as e:
        logger.error("❌ MongoDB lazy connect failed")
        logger.exception(e)
        db = None
        raise RuntimeError("MongoDB not available")


def get_db():
    if db is None:
        raise RuntimeError("❌ MongoDB not connected")
    return db
