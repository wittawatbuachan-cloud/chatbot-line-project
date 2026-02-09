# app/admin_router.py
import os
import json
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from config.logging_config import get_logger
from jobs.backup_jobs import backup_messages_collection, get_backup_metadata, fetch_backup_docs

logger = get_logger("admin", "logs/admin.log")

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# ADMIN_KEY must be set in environment (Render dashboard / .env)
ADMIN_KEY = os.getenv("ADMIN_KEY")


def _verify_admin(key: str | None):
    if not ADMIN_KEY:
        # If ADMIN_KEY is not configured, treat as forbidden to be safe
        raise HTTPException(status_code=500, detail="Admin key not configured on server")
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/backup/messages")
async def backup_messages(x_admin_key: str | None = Header(default=None)):
    """
    Trigger backup: copy messages -> messages_backup and store metadata.
    Header required: X-ADMIN-KEY
    """
    _verify_admin(x_admin_key)
    try:
        result = await backup_messages_collection(triggered_by="admin")
        return {"status": "ok", "backup": result}
    except Exception as e:
        logger.exception("❌ Backup failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backup/list")
async def list_backups(x_admin_key: str | None = Header(default=None)):
    """
    List backup metadata.
    Header required: X-ADMIN-KEY
    """
    _verify_admin(x_admin_key)
    try:
        docs = await get_backup_metadata(limit=200)
        return {"status": "ok", "backups": docs}
    except Exception as e:
        logger.exception("❌ List backups failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backup/download/{backup_id}")
async def download_backup(backup_id: str, x_admin_key: str | None = Header(default=None)):
    """
    Download a backup as JSON file.
    Header required: X-ADMIN-KEY
    """
    _verify_admin(x_admin_key)
    try:
        docs = await fetch_backup_docs(backup_id)
        if not docs:
            raise HTTPException(status_code=404, detail="Backup not found or empty")

        # stream JSON: convert to bytes
        def iter_json():
            # stream as a single JSON array (saves memory compared to joining large strings)
            yield "[".encode("utf-8")
            first = True
            for doc in docs:
                if not first:
                    yield ",".encode("utf-8")
                else:
                    first = False
                yield json.dumps(doc, ensure_ascii=False).encode("utf-8")
            yield "]".encode("utf-8")

        # Get a filename hint from metadata (optional)
        filename = f"messages_backup_{backup_id}.json"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        return StreamingResponse(iter_json(), media_type="application/json", headers=headers)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Download backup failed")
        raise HTTPException(status_code=500, detail=str(e))
