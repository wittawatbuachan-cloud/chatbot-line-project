import motor.motor_asyncio
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db")

client = None
db = None


async def connect_db():
    global client, db
    print("DEBUG mongo_uri =", settings.MONGO_URI)

    logger.info("🔌 Connecting to MongoDB...")

    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5000
    )

    await client.admin.command("ping")
    db = client[settings.mongo_db]

    logger.info("✅ MongoDB connected")


async def close_db():
    global client
    if client:
        client.close()
        logger.info("🔌 MongoDB disconnected")
