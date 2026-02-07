from pydantic_settings import BaseSettings
from pydantic import ConfigDict


async def connect_db():
    global client, db
    print("DEBUG mongo_uri =", settings.MONGO_URL)

    logger.info("🔌 Connecting to MongoDB...")

    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5000
    )

    await client.admin.command("ping")
    db = client[settings.mongo_db]

    logger.info("✅ MongoDB connected")
