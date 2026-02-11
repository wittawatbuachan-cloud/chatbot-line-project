# config/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger("db")

client: AsyncIOMotorClient | None = None
db = None


async def connect_db():
    global client, db

    logger.info("🔌 Connecting to MongoDB...")

    client = AsyncIOMotorClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000
    )

    # test connection
    await client.admin.command("ping")

    db = client[settings.mongo_db]

    logger.info("✅ MongoDB connected")


def get_db():
    if db is None:
        raise RuntimeError("❌ MongoDB not connected")
    return db


async def close_db():
    global client
    if client:
        client.close()
        logger.info("🔌 MongoDB disconnected")
