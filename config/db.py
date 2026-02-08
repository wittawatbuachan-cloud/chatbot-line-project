# config/db.py
import motor.motor_asyncio
from app.config import settings
import logging
from typing import Optional

logger = logging.getLogger("db")

client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
db = None


async def connect_db():
    """
    Connect MongoDB without crashing the app.
    If connection fails -> log error, keep app alive.
    """
    global client, db

    logger.info("🔌 Connecting to MongoDB...")

    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongo_uri,
            serverSelectionTimeoutMS=5000,
            tls=True,  # ชัดเจนไปเลย
        )

        # test connection
        await client.admin.command("ping")

        db = client[settings.mongo_db]
        logger.info("✅ MongoDB connected")

    except Exception as e:
        db = None
        logger.error("❌ MongoDB connection failed (app still running)")
        logger.exception(e)   # log stack trace แต่ไม่ raise


def get_db():
    """
    Use this in endpoints / jobs
    """
    if db is None:
        raise RuntimeError("❌ MongoDB not connected")
    return db


async def close_db():
    global client
    if client:
        client.close()
        logger.info("🔌 MongoDB disconnected")
