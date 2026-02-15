from config.db import get_db
from datetime import datetime, timezone

COLLECTION = "blocked_users"

async def is_blocked(user_hash: str) -> bool:
    db = get_db()
    user = await db[COLLECTION].find_one({"user_hash": user_hash})
    return user is not None


async def block_user(user_hash: str, reason: str = "manual"):
    db = get_db()
    await db[COLLECTION].insert_one({
        "user_hash": user_hash,
        "reason": reason,
        "created_at": datetime.now(timezone.utc),
        "blocked_by": "admin"
    })


async def unblock_user(user_hash: str):
    db = get_db()
    await db[COLLECTION].delete_one({"user_hash": user_hash})


async def list_blocked_users():
    db = get_db()
    cursor = db[COLLECTION].find({}, {"_id": 0})  # ไม่ส่ง _id กลับ
    return [doc async for doc in cursor]