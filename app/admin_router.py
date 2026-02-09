# app/admin_router.py
from fastapi import APIRouter, HTTPException
from jobs.backup_job import backup_messages_collection
from config.logging_config import get_logger
import os

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

logger = get_logger("admin", "logs/admin.log")


@router.post("/backup/messages")
async def backup_messages():
    """
    Manual backup messages collection
    """
    try:
        result = await backup_messages_collection()
        return {
            "status": "ok",
            "backup": result
        }

    except Exception as e:
        logger.exception("❌ Backup failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backup/files")
def list_backup_files():
    path = "backups"
    if not os.path.exists(path):
        return {"files": []}

    files = []
    for f in os.listdir(path):
        full = os.path.join(path, f)
        files.append({
            "name": f,
            "size": os.path.getsize(full)
        })

    return {"files": files}