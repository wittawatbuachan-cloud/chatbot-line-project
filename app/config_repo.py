# app/config_repo.py

from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import CONFIGS
from config.logging_config import get_logger

logger = get_logger("config_repo", "logs/config_repo.log")

SYSTEM_ID = "system"

# ✅ Default config (ใช้เฉพาะตอนยังไม่มีใน DB)
DEFAULT_CONFIG = {
    "_id": "system",
    "threshold_high": 0.8,
    "threshold_medium": 0.5,
    "emergency_numbers": ["1323", "1669"],
    "prompt_template": (
        "คุณคือผู้ช่วยด้านสุขภาพจิตที่พูดภาษาไทยอย่างเป็นธรรมชาติ "
        "น้ำเสียงอบอุ่น อ่อนโยน เข้าใจความรู้สึก "
        "ห้ามใช้ภาษาทางการเกินไป "
        "ห้ามใช้ศัพท์วิชาการยาก "
        "ตอบสั้น กระชับ เข้าใจง่าย "
        "ถ้าผู้ใช้มีความเสี่ยงสูง ให้แนะนำสายด่วนอย่างสุภาพ "
        "ห้ามวินิจฉัยโรค "
        "ห้ามให้คำแนะนำทางการแพทย์เชิงลึก "
        "ตอบกลับเป็น JSON เท่านั้นในรูปแบบ: "
        "{ emotion: string, risk_level: low|medium|high, reply: string }"
    ),
    "canned_responses": {
        "high": (
            "ฉันเป็นห่วงคุณมาก หากคุณรู้สึกไม่ปลอดภัย "
            "โปรดติดต่อสายด่วนสุขภาพจิต 1323 "
            "หรือ 1669 หากเป็นเหตุฉุกเฉิน"
        ),
        "medical_block": (
            "ขออภัย ฉันไม่สามารถให้คำแนะนำทางการแพทย์ได้ "
            "กรุณาปรึกษาผู้เชี่ยวชาญโดยตรง"
        )
    },
    "updated_at": datetime.utcnow()
}

# ✅ ดึง config และสร้าง default ถ้าไม่มี
async def get_system_config():
    config = await db[CONFIGS].find_one({"_id": SYSTEM_ID})

    if not config:
        logger.warning("⚠ System config not found. Creating default.")
        await db[CONFIGS].insert_one(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    return config


# ✅ อัปเดต thresholds
async def update_thresholds(low: float, medium: float, high: float):
    await db[CONFIGS].update_one(
        {"_id": SYSTEM_ID},
        {
            "$set": {
                "risk_thresholds.low": low,
                "risk_thresholds.medium": medium,
                "risk_thresholds.high": high,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )

    logger.info("✅ Risk thresholds updated")


# ✅ อัปเดตเบอร์ฉุกเฉิน
async def update_emergency_numbers(numbers: list[str]):
    await db[CONFIGS].update_one(
        {"_id": SYSTEM_ID},
        {
            "$set": {
                "emergency_numbers": numbers,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )

    logger.info("✅ Emergency numbers updated")


# ✅ อัปเดต canned response
async def update_safety_ack(message: str):
    await db[CONFIGS].update_one(
        {"_id": SYSTEM_ID},
        {
            "$set": {
                "canned_responses.safety_ack": message,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )

    logger.info("✅ Safety acknowledgment updated")
