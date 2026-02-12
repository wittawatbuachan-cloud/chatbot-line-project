# app/admin_audit.py

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from config.db import get_db
from config.logging_config import get_logger
import os

router = APIRouter(prefix="/admin", tags=["admin-audit"])
logger = get_logger("admin_audit", "logs/admin_audit.log")

ADMIN_KEY = os.getenv("ADMIN_KEY")


def verify_admin(x_admin_key: str | None = Header(default=None)):

    if not ADMIN_KEY:
        raise HTTPException(status_code=500, detail="Admin auth not configured")

    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return True


@router.get("/audit_logs")
async def get_audit_logs(
    action: str | None = Query(None),
    actor: str | None = Query(None),
    limit: int = 100,
    auth: bool = Depends(verify_admin)
):

    db = get_db()
    query = {}

    if action:
        query["action"] = action

    if actor:
        query["actor"] = actor

    cursor = db.audit_logs.find(query).sort("created_at", -1).limit(limit)

    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)

    return {
        "count": len(results),
        "data": results
    }
