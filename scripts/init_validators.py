import asyncio
from config.db import connect_db, close_db, get_db


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

    await db.command({
        "collMod": "conversations",
        "validator": validator,
        "validationLevel": "moderate"
    })

    print("✅ conversations validator applied")


async def main():
    await connect_db()
    await apply_conversation_validator()
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
