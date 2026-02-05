# tests/test_db.py
import asyncio

from app.message_repo import (
    insert_message,
    get_timeline,
    count_messages
)
from config.db import check_db_connection


USER_HASH = "demo_user_hash"
SESSION_ID = "demo_session_001"


async def run_test():
    print("🔌 Checking MongoDB connection...")
    await check_db_connection()
    print("✅ MongoDB connected\n")

    # -------------------------
    # Insert messages
    # -------------------------
    print("✍️ Inserting messages...")

    await insert_message(
        user_hash=USER_HASH,
        session_id=SESSION_ID,
        role="user",
        content="สวัสดีครับ ผมกำลังทดสอบระบบ"
    )

    await insert_message(
        user_hash=USER_HASH,
        session_id=SESSION_ID,
        role="assistant",
        content="สวัสดีครับ ระบบเชื่อมต่อ MongoDB เรียบร้อยแล้ว"
    )

    print("✅ Insert messages success\n")

    # -------------------------
    # Load timeline
    # -------------------------
    print("📜 Loading conversation timeline...")

    timeline = await get_timeline(
        user_hash=USER_HASH,
        session_id=SESSION_ID
    )

    for i, msg in enumerate(timeline, start=1):
        print(f"{i}. [{msg['role']}] {msg['content']} ({msg['timestamp']})")

    print("\n✅ Timeline loaded\n")

    # -------------------------
    # Count messages
    # -------------------------
    total = await count_messages(SESSION_ID)
    print(f"📊 Total messages in session: {total}\n")

    print("🎉 DB test completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_test())
