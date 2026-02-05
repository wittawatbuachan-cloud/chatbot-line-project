# config/db.py
import motor.motor_asyncio
import logging
from app.config import settings

logger = logging.getLogger("db")

client: motor.motor_asyncio.AsyncIOMotorClient | None = None
db = None

async def connect_db():
    global client, db

    print("🔥 ENTER connect_db()")

    print("🔥 mongo_uri =", settings.mongo_uri)

    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5000
    )

    print("🔥 client created")

    await client.admin.command("ping")
    print("🔥 ping ok")

    db = client[settings.mongo_db]
    print("🔥 db selected", settings.mongo_db)

    print("✅ MongoDB connected")

