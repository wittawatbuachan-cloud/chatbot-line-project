# config/db.py
import motor.motor_asyncio
import logging
from app.config import settings

logger = logging.getLogger("db")

client: motor.motor_asyncio.AsyncIOMotorClient | None = None
db = None

async def connect_db():
    global client, db
    logger.info("🔌 Connecting to MongoDB...")

    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5000
    )

    # บังคับ test connection
    await client.admin.command("ping")

    db = client[settings.mongo_db]
    logger.info("✅ MongoDB connected")

async def close_db():
    global client
    if client:
        client.close()
        logger.info("🔌 MongoDB disconnected")
