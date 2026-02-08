# config/db.py
import motor.motor_asyncio
from app.config import settings
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db")

client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
db = None

async def connect_db():
    global client, db
    logger.info("🔌 Connecting to MongoDB...")

    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongo_uri,
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
