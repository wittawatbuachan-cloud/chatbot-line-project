# test_db.py
import asyncio
from app.db import (
    insert_conversation,
    append_conversation_session,
    create_incident
)

async def test_insert_all():
    user_hash = "user_test_001"
    session_id = "session_test_001"

    print("▶ Test: insert_conversation")
    conv_id = await insert_conversation(
        user_hash=user_hash,
        session_id=session_id,
        message={
            "role": "user",
            "text": "สวัสดีครับ ผมรู้สึกเครียดมาก"
        }
    )
    print("✔ inserted conversation_id:", conv_id)

    print("\n▶ Test: append_conversation_session")
    msg_id = await append_conversation_session(
        user_hash=user_hash,
        session_id=session_id,
        role="assistant",
        text="ขอบคุณที่เล่าให้ฟังนะครับ ผมอยู่ตรงนี้กับคุณ",
        sentiment="negative",
        risk_score=0.72
    )
    print("✔ inserted message_id:", msg_id)

    print("\n▶ Test: create_incident")
    incident_id = await create_incident(
        user_hash=user_hash,
        session_id=session_id,
        risk_score=0.85,
        keywords=["เครียด", "หมดหวัง", "นอนไม่หลับ"]
    )
    print("✔ inserted incident_id:", incident_id)

    print("\n🎉 All MongoDB tests passed!")

if __name__ == "__main__":
    asyncio.run(test_insert_all())
