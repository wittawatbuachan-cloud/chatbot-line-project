import motor.motor_asyncio
from app.config import settings

client = None
db = None

async def connect_db():
    global client, db

    print("🔥 ENTER connect_db()")
    print("🔥 mongo_uri =", settings.mongo_uri)

    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5000
    )

    await client.admin.command("ping")
    db = client[settings.mongo_db]

    print("✅ MongoDB connected")

async def close_db():
    global client
    if client:
        client.close()
        print("🔌 MongoDB disconnected")
