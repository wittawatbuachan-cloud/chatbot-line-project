# app/admin_router.py
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from config.logging_config import get_logger
from jobs.backup_job import (
    backup_messages_collection,
    get_backup_metadata,
    fetch_backup_docs,
)

logger = get_logger("admin", "logs/admin.log")

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# 🔒 ปิด admin เมื่อ deploy production จริง
DEBUG = True   # 🔴 ถ้าจะปิด admin เปลี่ยนเป็น False


def _verify_admin():
    if not DEBUG:
        raise HTTPException(
            status_code=403,
            detail="Admin endpoints are disabled"
        )


@router.post("/backup/messages")
async def backup_messages():
    _verify_admin()
    try:
        result = await backup_messages_collection(triggered_by="admin")
        return {"status": "ok", "backup": result}
    except Exception as e:
        logger.exception("❌ Backup failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backup/list")
async def list_backups():
    _verify_admin()
    try:
        docs = await get_backup_metadata(limit=200)
        return {"status": "ok", "backups": docs}
    except Exception as e:
        logger.exception("❌ List backups failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backup/download/{backup_id}")
async def download_backup(backup_id: str):
    _verify_admin()
    try:
        docs = await fetch_backup_docs(backup_id)
        if not docs:
            raise HTTPException(status_code=404, detail="Backup not found")

        def iter_json():
            yield "[".encode("utf-8")
            first = True
            for doc in docs:
                if not first:
                    yield ",".encode("utf-8")
                first = False
                yield json.dumps(doc, ensure_ascii=False).encode("utf-8")
            yield "]".encode("utf-8")

        headers = {
            "Content-Disposition": f'attachment; filename="messages_backup_{backup_id}.json"'
        }
        return StreamingResponse(
            iter_json(),
            media_type="application/json",
            headers=headers
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Download backup failed")
        raise HTTPException(status_code=500, detail=str(e))
