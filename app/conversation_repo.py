# app/conversation_repo.py

from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import CONVERSATIONS


# =====================================================
# CREATE CONVERSATION (ถ้ายังไม่มี)
# =====================================================
async def create_conversation(
    user_hash: str,
    session_id: str,
    platform: str = "LINE",
    language: str = "th"
):
    now = datetime.now(timezone.utc)

    existing = await db[CONVERSATIONS].find_one({"session_id": session_id})
    if existing:
        return str(existing["_id"])

    doc = {
        "user_hash": user_hash,
        "session_id": session_id,
        "created_at": now,
        "last_active": now,
        "meta": {
            "platform": platform,
            "language": language
        },
        "messages": []
    }

    result = await db[CONVERSATIONS].insert_one(doc)
    return str(result.inserted_id)


# =====================================================
# ADD MESSAGE (embedded)
# =====================================================
async def add_message(
    session_id: str,
    role: str,
    text: str,
    sentiment: str | None = None,
    risk_score: float | None = None
):
    now = datetime.now(timezone.utc)

    message_doc = {
        "role": role,        # user / assistant
        "content": text,     # 🔥 เปลี่ยนจาก text → content ให้สอดคล้อง LLM
        "ts": now,
        "sentiment": sentiment,
        "risk_score": risk_score
    }

    result = await db[CONVERSATIONS].update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": message_doc},
            "$set": {"last_active": now}
        }
    )

    # ถ้า session ไม่มี → สร้างใหม่
    if result.matched_count == 0:
        await create_conversation(
            user_hash="unknown",
            session_id=session_id
        )
        await db[CONVERSATIONS].update_one(
            {"session_id": session_id},
            {"$push": {"messages": message_doc}}
        )


# =====================================================
# GET RECENT CONTEXT (สำคัญที่สุด)
# =====================================================
async def get_recent_context(
    session_id: str,
    limit: int = 5
):
    """
    ดึงข้อความย้อนหลัง limit ข้อ
    เรียงจากเก่า → ใหม่
    """

    conversation = await db[CONVERSATIONS].find_one(
        {"session_id": session_id},
        {"messages": {"$slice": -limit}}
    )

    if not conversation:
        return []

    messages = conversation.get("messages", [])

    # format ให้พร้อมเข้า prompt
    formatted = []
    for msg in messages:
        formatted.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    return formatted
