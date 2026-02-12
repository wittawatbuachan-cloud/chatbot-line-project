# scripts/init_collections.py

import asyncio
from datetime import datetime
from config.db import connect_db, close_db, get_db


# ==============================
# CREATE COLLECTIONS + INDEXES
# ==============================

async def create_collections():
    db = get_db()

    existing = await db.list_collection_names()

    # --------------------------
    # 1️⃣ conversations
    # --------------------------
    if "conversations" not in existing:
        await db.create_collection("conversations")
        print("✅ Created conversations")

    await db.conversations.create_index("user_hash")
    await db.conversations.create_index("session_id", unique=True)
    await db.conversations.create_index("last_active")

    # --------------------------
    # 2️⃣ incidents
    # --------------------------
    if "incidents" not in existing:
        await db.create_collection("incidents")
        print("✅ Created incidents")

    await db.incidents.create_index("user_hash")
    await db.incidents.create_index("session_id")
    await db.incidents.create_index("risk_score")
    await db.incidents.create_index("status")
    await db.incidents.create_index("trigger_ts")

    # --------------------------
    # 3️⃣ configs
    # --------------------------
    if "configs" not in existing:
        await db.create_collection("configs")
        print("✅ Created configs")


    # create default system config if not exists
    system_config = await db.configs.find_one({"_id": "system"})
    if not system_config:
        await db.configs.insert_one({
            "_id": "system",
            "risk_thresholds": {
                "low": 0.3,
                "medium": 0.5,
                "high": 0.8
            },
            "emergency_numbers": ["1323", "1669"],
            "canned_responses": {
                "safety_ack": "ระบบตรวจพบความเสี่ยง กรุณาติดต่อสายด่วนสุขภาพจิต 1323"
            },
            "updated_at": datetime.utcnow()
        })
        print("✅ Inserted default system config")

    # --------------------------
    # 4️⃣ audit_logs
    # --------------------------
    if "audit_logs" not in existing:
        await db.create_collection("audit_logs")
        print("✅ Created audit_logs")

    await db.audit_logs.create_index("action")
    await db.audit_logs.create_index("actor")
    await db.audit_logs.create_index("timestamp")

    print("\n🎉 All collections initialized successfully")


# ==============================
# APPLY JSON VALIDATOR
# ==============================

async def apply_conversation_validator():
    db = get_db()

    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_hash", "session_id", "messages", "created_at"],
            "properties": {
                "user_hash": {"bsonType": "string"},
                "session_id": {"bsonType": "string"},
                "created_at": {"bsonType": "date"},
                "last_active": {"bsonType": ["date", "null"]},
                "meta": {
                    "bsonType": "object",
                    "properties": {
                        "platform": {"bsonType": "string"},
                        "language": {"bsonType": "string"}
                    }
                },
                "messages": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "required": ["role", "text", "ts"],
                        "properties": {
                            "role": {"bsonType": "string"},
                            "text": {"bsonType": "string"},
                            "ts": {"bsonType": "date"},
                            "sentiment": {"bsonType": ["string", "null"]},
                            "risk_score": {"bsonType": ["double", "null"]}
                        }
                    }
                }
            }
        }
    }

    try:
        await db.command({
            "collMod": "conversations",
            "validator": validator,
            "validationLevel": "moderate"
        })
        print("✅ Applied conversations validator")
    except Exception as e:
        print("⚠️ Validator apply skipped:", e)


# ==============================
# MAIN
# ==============================

async def main():
    await connect_db()

    await create_collections()
    await apply_conversation_validator()

    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
