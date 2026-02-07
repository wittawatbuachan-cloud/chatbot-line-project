# config/db.py
import motor.motor_asyncio
from app.config import settings
import logging

logger = logging.getLogger("db")

client = None
db = None

async def connect_db():
    global client, db
    logger.info("🔌 Connecting to MongoDB...")

    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5000
    )

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
