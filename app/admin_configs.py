# app/admin_configs.py

from fastapi import APIRouter, Depends, Header, HTTPException
from app.configs_repo import get_system_config, update_system_config
from app.audit_repo import log_action
from config.logging_config import get_logger
import os

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger("admin_configs", "logs/admin_configs.log")

ADMIN_KEY = os.getenv("ADMIN_KEY")

def verify_admin(x_admin_key: str = Header(...)):
    if not ADMIN_KEY:
        logger.error("ADMIN_KEY not set in environment")
        raise HTTPException(status_code=500, detail="Admin authentication not configured")

    if x_admin_key != ADMIN_KEY:
        logger.warning("Unauthorized admin access attempt")
        raise HTTPException(status_code=403, detail="Unauthorized")

    return x_admin_key


@router.get("/configs")
async def read_configs(actor: str = Depends(verify_admin)):
    config = await get_system_config()
    return config


@router.post("/configs")
async def write_configs(payload: dict, actor: str = Depends(verify_admin)):

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

    updated_config = update_system_config(filtered_payload)

    # บันทึก audit
    await log_action(
        action="update_config",
        actor=actor,
        detail={"updated_fields": list(filtered_payload.keys())},
        target_type="config",
        target_id="system"
    )

    return {
        "status": "updated",
        "config": updated_config
    }
