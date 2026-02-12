# app/admin_dashboard.py
from app.audit_repo import log_action
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from config.db import get_db
from config.logging_config import get_logger
from datetime import datetime, timedelta, timezone
from typing import Optional
from bson import ObjectId
import os

router = APIRouter(prefix="/admin", tags=["admin-dashboard"])
logger = get_logger("admin_dashboard", "logs/admin_dashboard.log")

ADMIN_KEY = os.getenv("ADMIN_KEY")


# =========================
# AUTH
# =========================

def verify_admin(x_admin_key: str | None = Header(default=None)):

    if not ADMIN_KEY:
        raise HTTPException(status_code=500, detail="Admin auth not configured")

    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return True


# =========================================================
# 3.4.1 — GET INCIDENTS
# =========================================================

@router.get("/incidents")
async def get_incidents(
    status: Optional[str] = Query(None),
    min_risk: Optional[float] = Query(None),
    limit: int = 50,
    auth: bool = Depends(verify_admin)
):

    db = get_db()
    query = {}

    if status:
        query["status"] = status

    if min_risk is not None:
        query["risk_score"] = {"$gte": min_risk}

    cursor = db.incidents.find(query).sort("trigger_ts", -1).limit(limit)

    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)

    return {
        "count": len(results),
        "data": results
    }


# =========================================================
# 3.4.2 — HANDLE INCIDENT
# =========================================================

@router.post("/handle")
async def handle_incident(
    incident_id: str,
    action: str,  # in_progress / closed
    admin_name: str,
    note: Optional[str] = None,
    actor: str = Depends(verify_admin)
):

    if action not in ["in_progress", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    db = get_db()

    update_doc = {
        "status": action,
        "handled_by": admin_name,
        "notes": note,
        "handled_ts": datetime.now(timezone.utc)
    }

    result = await db.incidents.update_one(
        {"_id": ObjectId(incident_id)},
        {"$set": update_doc}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Incident not found")

    # ✅ บันทึก audit
    await log_action(
        action="handle_incident",
        actor=actor,
        detail={
            "incident_id": incident_id,
            "new_status": action,
            "note": note
        },
        target_type="incident",
        target_id=incident_id
    )

    logger.info(f"Incident {incident_id} updated to {action}")

    return {
        "message": f"Incident updated to {action}"
    }


# =========================================================
# 3.4.3 — STATS ENDPOINT
# =========================================================

@router.get("/stats")
async def get_admin_stats(
    days: int = 7,
    auth: bool = Depends(verify_admin)
):

    db = get_db()
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # total incidents
    total_incidents = await db.incidents.count_documents({
        "trigger_ts": {"$gte": since}
    })

    # status distribution
    status_pipeline = [
        {"$match": {"trigger_ts": {"$gte": since}}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]

    status_counts = {}
    async for doc in db.incidents.aggregate(status_pipeline):
        status_counts[doc["_id"]] = doc["count"]

    # average risk score
    risk_pipeline = [
        {"$match": {"trigger_ts": {"$gte": since}}},
        {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}}
    ]

    avg_risk = 0.0
    async for doc in db.incidents.aggregate(risk_pipeline):
        avg_risk = round(doc["avg_risk"], 3)

    # top keywords
    keyword_pipeline = [
        {"$match": {"trigger_ts": {"$gte": since}}},
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]

    top_keywords = []
    async for doc in db.incidents.aggregate(keyword_pipeline):
        top_keywords.append({
            "keyword": doc["_id"],
            "count": doc["count"]
        })

    return {
        "period_days": days,
        "total_incidents": total_incidents,
        "status_distribution": status_counts,
        "average_risk_score": avg_risk,
        "top_keywords": top_keywords
    }
