from app.gemini_client import generate_empathetic_response
from config.db import get_db
from datetime import datetime
from config.logging_config import get_logger

logger = get_logger("ai_service", "logs/ai_service.log")


async def generate_reply(user_id: str, user_message: str):

    result = await generate_empathetic_response(user_message)

    db = get_db()

    # บันทึกข้อความปกติ
    await db.messages.insert_one({
        "user_id": user_id,
        "message": user_message,
        "emotion": result["emotion"],
        "risk_level": result["risk_level"],
        "reply": result["reply"],
        "timestamp": datetime.utcnow()
    })

    # 🔥 ถ้า HIGH RISK
    if result["risk_level"] == "high":

        logger.warning(f"HIGH RISK DETECTED from {user_id}")

        await db.high_risk_cases.insert_one({
            "user_id": user_id,
            "message": user_message,
            "emotion": result["emotion"],
            "risk_level": result["risk_level"],
            "timestamp": datetime.utcnow(),
            "status": "pending_review"
        })

    return result["reply"]
