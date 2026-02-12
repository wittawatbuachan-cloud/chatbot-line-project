# app/admin_metrics.py

from fastapi import APIRouter, Depends, Header, HTTPException
from config.db import get_db
from config.logging_config import get_logger
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["metrics"])
logger = get_logger("admin_metrics", "logs/admin_metrics.log")

ADMIN_KEY = os.getenv("ADMIN_KEY")


def verify_admin(x_admin_key: str | None = Header(default=None)):

    if not ADMIN_KEY:
        raise HTTPException(status_code=500, detail="Admin auth not configured")

    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return True


@router.get("/metrics/summary")
async def metrics_summary(auth: bool = Depends(verify_admin)):

    db = get_db()
    since = datetime.utcnow() - timedelta(days=7)

    total_messages = await db.metrics.count_documents({
        "created_at": {"$gte": since}
    })

    high_risk = await db.metrics.count_documents({
        "risk_level": "high",
        "created_at": {"$gte": since}
    })

    errors = await db.metrics.count_documents({
        "success": False,
        "created_at": {"$gte": since}
    })

    return {
        "last_7_days": {
            "total_messages": total_messages,
            "high_risk": high_risk,
            "errors": errors
        }
    }
