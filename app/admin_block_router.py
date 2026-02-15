from fastapi import APIRouter, Header, HTTPException
from app.block_repo import block_user, unblock_user, is_blocked
from app.config import settings
from app.block_repo import list_blocked_users

router = APIRouter(prefix="/admin", tags=["admin"])

def verify_admin_key(x_admin_key: str | None):
    if not x_admin_key or x_admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/block")
async def admin_block(
    user_hash: str,
    reason: str = "manual",
    x_admin_key: str | None = Header(default=None)
):
    verify_admin_key(x_admin_key)

    if await is_blocked(user_hash):
        return {"status": "already_blocked"}

    await block_user(user_hash, reason)
    return {"status": "blocked", "user_hash": user_hash}


@router.post("/unblock")
async def admin_unblock(
    user_hash: str,
    x_admin_key: str | None = Header(default=None)
):
    verify_admin_key(x_admin_key)

    await unblock_user(user_hash)
    return {"status": "unblocked", "user_hash": user_hash}


@router.get("/blocked")
async def admin_list_blocked(
    x_admin_key: str | None = Header(default=None)
):
    verify_admin_key(x_admin_key)

    users = await list_blocked_users()
    return {
        "count": len(users),
        "blocked_users": users
    }