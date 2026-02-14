# app/configs_repo.py

from datetime import datetime, timezone
from typing import Dict, Any
from config.db import get_db
from config.logging_config import get_logger

logger = get_logger("configs_repo", "logs/configs_repo.log")


def _default_system_doc() -> Dict[str, Any]:
    return {
        "_id": "system",
        "threshold_high": 0.8,
        "threshold_medium": 0.5,
        "emergency_numbers": ["1323", "1669"],
        "prompt_template": (
            "คุณคือผู้ช่วยด้านสุขภาพจิตที่พูดภาษาไทยอย่างเป็นธรรมชาติ\n"
            "น้ำเสียง: อบอุ่น อ่อนโยน และเข้าใจความรู้สึก\n"
            "กฎความปลอดภัย: ห้ามวินิจฉัยโรค และห้ามให้คำแนะนำทางการแพทย์เชิงลึก\n"
            "หากพบความเสี่ยงสูง ให้แนะนำสายด่วน 1323 หรือ 1669 อย่างสุภาพ\n"
            "ตอบกลับเป็น JSON เท่านั้นในรูปแบบ: { \"emotion\": string, \"risk_level\": \"low|medium|high\", \"reply\": string }"
        ),
        "few_shot_examples": "",
        "canned_responses": {
            "high": "หากคุณคิดจะทำร้ายตัวเองหรือรู้สึกไม่ปลอดภัย โปรดติดต่อสายด่วน 1323 หรือ 1669 ทันที",
            "medical_block": "ขออภัย ฉันไม่สามารถให้คำแนะนำทางการแพทย์เชิงลึกได้ หากต้องการคำปรึกษาเพิ่มเติม โปรดปรึกษาผู้เชี่ยวชาญ"
        },
        "updated_at": datetime.now(timezone.utc)
    }


async def seed_system_config_if_missing() -> Dict[str, Any]:
    """
    Ensure there is a system config document in the `configs` collection.
    If missing, insert a default document and return it.
    """
    db = get_db()
    doc = await db.configs.find_one({"_id": "system"})
    if doc:
        return doc

    default_doc = _default_system_doc()
    # Convert datetime to naive UTC if necessary (motor handles datetimes)
    try:
        await db.configs.insert_one(default_doc)
        logger.info("Seeded default system config into `configs` collection")
    except Exception:
        logger.exception("Failed to seed system config")
        # try to fetch again
    doc = await db.configs.find_one({"_id": "system"})
    if not doc:
        # As a last resort, return the default doc (not stored)
        logger.warning("System config not stored but returning default in-memory")
        return default_doc
    return doc


async def get_system_config() -> Dict[str, Any]:
    """
    Retrieve system configuration for prompts and thresholds.
    Auto-seed a default document if not present.
    """
    db = get_db()
    doc = await db.configs.find_one({"_id": "system"})
    if doc:
        return doc

    # seed default and return
    return await seed_system_config_if_missing()


async def update_system_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update fields in the system config doc. Returns the updated document.
    Only updates top-level keys provided in `updates`.
    """
    if not updates:
        raise ValueError("No updates provided")

    db = get_db()
    updates = updates.copy()
    updates["updated_at"] = datetime.now(timezone.utc)

    # Upsert the document
    result = await db.configs.update_one(
        {"_id": "system"},
        {"$set": updates},
        upsert=True
    )

    # Return the newly stored doc
    doc = await db.configs.find_one({"_id": "system"})
    if not doc:
        # fallback to building dict
        doc = _default_system_doc()
        doc.update(updates)
    logger.info("System config updated: %s", list(updates.keys()))
    return doc