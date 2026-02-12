# app/admin_configs.py

from fastapi import APIRouter, Depends, Header, HTTPException
from app.configs_repo import get_system_config, update_system_config
from config.logging_config import get_logger
import os

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger("admin_configs", "logs/admin_configs.log")

ADMIN_KEY = os.getenv("ADMIN_KEY")


# 🔐 Admin Authentication
def verify_admin(x_admin_key: str | None = Header(default=None)):

    if not ADMIN_KEY:
        logger.error("ADMIN_KEY not set in environment")
        raise HTTPException(status_code=500, detail="Admin authentication not configured")

    if x_admin_key != ADMIN_KEY:
        logger.warning("Unauthorized admin access attempt")
        raise HTTPException(status_code=403, detail="Unauthorized")

    return True


# 🔎 GET current config
@router.get("/configs")
async def read_configs(auth: bool = Depends(verify_admin)):
    config = await get_system_config()
    return config


# ✏ UPDATE config
@router.post("/configs")
async def write_configs(payload: dict, auth: bool = Depends(verify_admin)):

    allowed_fields = {
        "threshold_high",
        "threshold_medium",
        "emergency_numbers",
        "prompt_template",
        "canned_responses"
    }

    filtered_payload = {
        key: value for key, value in payload.items()
        if key in allowed_fields
    }

    if not filtered_payload:
        raise HTTPException(
            status_code=400,
            detail="No valid config fields provided"
        )

    updated_config = await update_system_config(filtered_payload)

    return {
        "status": "updated",
        "config": updated_config
    }
