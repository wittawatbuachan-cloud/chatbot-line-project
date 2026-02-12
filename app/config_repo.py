# app/config_repo.py

from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import CONFIGS
from config.logging_config import get_logger

logger = get_logger("config_repo", "logs/config_repo.log")

SYSTEM_ID = "system"

# ✅ Default config (ใช้เฉพาะตอนยังไม่มีใน DB)
DEFAULT_CONFIG = {
    "_id": SYSTEM_ID,
    "risk_thresholds": {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.8
    },
    "emergency_numbers": ["1323", "1669"],
    "canned_responses": {
        "safety_ack": "ฉันเป็นห่วงคุณมาก หากคุณรู้สึกไม่ปลอดภัย โปรดโทร 1323",
        "medical_block": "ขออภัย ฉันไม่สามารถให้คำแนะนำทางการแพทย์ได้"
    },
    "updated_at": datetime.now(timezone.utc)
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
