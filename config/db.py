# config/db.py

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger("db")

# โหลด .env (สำหรับ local)
load_dotenv()

client: AsyncIOMotorClient | None = None
db = None


def get_mongo_settings():
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB", "chatbot_db")

    if not mongo_uri:
        logger.error("❌ MONGO_URI not found in environment variables")
        raise RuntimeError("MONGO_URI not found in environment variables")

    return mongo_uri, mongo_db


async def connect_db():
    global client, db

    logger.info("🔌 Connecting to MongoDB...")

    mongo_uri, mongo_db = get_mongo_settings()

    try:
        client = AsyncIOMotorClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000
        )

        # test connection
        await client.admin.command("ping")

        db = client[mongo_db]

        logger.info("✅ MongoDB connected successfully")

    except Exception as e:
        logger.exception("❌ MongoDB connection failed")
        raise e


def get_db():
    if db is None:
        raise RuntimeError("❌ MongoDB not connected. Did you call connect_db()?")

    return db


async def close_db():
    global client

    if client:
        client.close()
        logger.info("🔌 MongoDB disconnected")
