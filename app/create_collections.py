# app/create_collections.py

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB", "chatbot_db")


async def create_indexes():
    print("MONGO_URI =", MONGO_URI)

    if not MONGO_URI:
        raise RuntimeError("❌ MONGO_URI not found in environment variables")

    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # ===== METRICS =====
    await db.metrics.create_index("created_at")
    await db.metrics.create_index("risk_level")
    await db.metrics.create_index("success")

    # ===== CONFIGS =====
    await db.configs.create_index("updated_at")

    # ===== CONVERSATIONS =====
    await db.conversations.create_index("user_hash")
    await db.conversations.create_index("created_at")

    # ===== MESSAGES =====
    await db.messages.create_index("conversation_id")
    await db.messages.create_index("created_at")

    # ===== INCIDENTS =====
    await db.incidents.create_index("user_hash")
    await db.incidents.create_index("risk_level")
    await db.incidents.create_index("created_at")

    # ===== AUDIT LOGS =====
    await db.audit_logs.create_index("created_at")

    print("✅ All collections & indexes created successfully")

    client.close()


if __name__ == "__main__":
    asyncio.run(create_indexes())
