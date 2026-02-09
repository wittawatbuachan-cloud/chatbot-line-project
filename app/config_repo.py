# app/config_repo.py
from datetime import datetime, timezone
from config.db import db
from app.mongo_collections import CONFIGS

async def set_config(key: str, value):
    await db[CONFIGS].update_one(
        {"key": key},
        {
            "$set": {
                "value": value,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )

async def get_config(key: str):
    return await db[CONFIGS].find_one({"key": key})
