# config/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger("db")
load_dotenv()

# Environment variable names used by this project:
# - MONGODB_URI (preferred)
# - MONGO_DB (optional, default 'chatbot')
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "chatbot_db")

client: AsyncIOMotorClient | None = None
db = None

async def connect_db():
    """
    Async connect to MongoDB using motor.
    Call this in FastAPI startup.
    """
    global client, db
    if not MONGODB_URI:
        logger.error("MONGODB_URI not configured in environment")
        raise RuntimeError("MONGODB_URI not configured")

    logger.info("🔌 Connecting to MongoDB (motor)...")
    client = AsyncIOMotorClient(MONGODB_URI)
    try:
        # Ping to verify connection
        await client.admin.command("ping")
        db = client[MONGO_DB]
        logger.info("✅ MongoDB connected")
    except Exception as e:
        logger.exception("❌ MongoDB connection failed")
        # close client if something failed
        try:
            client.close()
        except Exception:
            pass
        client = None
        db = None
        raise

def get_db():
    """
    Return connected motor db instance.
    Raise if not connected.
    """
    if db is None:
        raise RuntimeError("❌ MongoDB not connected. Did you call connect_db() on startup?")
    return db

async def close_db():
    global client
    if client:
        client.close()
        logger.info("🔌 MongoDB disconnected")
        client = None