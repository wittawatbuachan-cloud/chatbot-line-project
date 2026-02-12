# app/create_collections.py

import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# โหลด .env (สำหรับ local)
load_dotenv()

DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "365"))


async def create_indexes():
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB", "chatbot_db")

    print("🔍 MONGO_URI =", mongo_uri)
    print("📦 DB_NAME =", db_name)
    print("🗓 DATA_RETENTION_DAYS =", DATA_RETENTION_DAYS)

    if not mongo_uri:
        raise RuntimeError("❌ MONGO_URI not found in environment variables")

    client = AsyncIOMotorClient(
        mongo_uri,
        serverSelectionTimeoutMS=5000
    )

    try:
        # ทดสอบเชื่อมต่อ
        await client.admin.command("ping")
        print("✅ MongoDB connection OK")

        db = client[db_name]

        # ==================================================
        # METRICS
        # ==================================================
        await db.metrics.create_index("created_at")
        await db.metrics.create_index("risk_level")
        await db.metrics.create_index("success")

        # ==================================================
        # CONFIGS
        # ==================================================
        await db.configs.create_index("updated_at")

        # ==================================================
        # CONVERSATIONS
        # ==================================================
        await db.conversations.create_index("user_hash")
        await db.conversations.create_index("session_id", unique=True)
        await db.conversations.create_index("created_at")

        # ==================================================
        # MESSAGES
        # ==================================================
        await db.messages.create_index("conversation_id")
        await db.messages.create_index("created_at")

        # TTL (auto delete)
        await db.messages.create_index(
            "created_at",
            expireAfterSeconds=DATA_RETENTION_DAYS * 24 * 60 * 60,
            name="ttl_created_at"
        )

        # ==================================================
        # INCIDENTS
        # ==================================================
        await db.incidents.create_index("user_hash")
        await db.incidents.create_index("risk_score")
        await db.incidents.create_index("status")
        await db.incidents.create_index("trigger_ts")

        # ==================================================
        # AUDIT LOGS
        # ==================================================
        await db.audit_logs.create_index("created_at")
        await db.audit_logs.create_index("actor")
        await db.audit_logs.create_index("action")

        print("🎉 All collections & indexes created successfully")

    except Exception as e:
        print("❌ Error creating indexes:", e)
        raise e

    finally:
        client.close()
        print("🔌 MongoDB connection closed")


if __name__ == "__main__":
    asyncio.run(create_indexes())
