# app/config_repo.py

from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import CONFIGS

SYSTEM_ID = "system"


async def get_system_config():
    return await db[CONFIGS].find_one({"_id": SYSTEM_ID})


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
