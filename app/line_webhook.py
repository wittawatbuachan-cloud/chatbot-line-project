# app/line_webhook.py
from fastapi import APIRouter, Request, Header, HTTPException
from app.message_repo import insert_message
from app.anonymizer import hash_user
from app.line_reply import reply_message
from config.db import get_db
from config.logging_config import get_logger
import hmac
import hashlib
import base64
import os

LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")

def verify_signature(body: bytes, signature: str | None):
    if not signature or not LINE_SECRET:
        return False

    hash_bytes = hmac.new(
        LINE_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()

    return base64.b64encode(hash_bytes).decode() == signature

router = APIRouter()
logger = get_logger("line_webhook", "logs/line_webhook.log")

@router.post("/callback")
async def line_callback(
    request: Request,
    x_line_signature: str | None = Header(default=None)
):
    raw_body = await request.body()

    if not verify_signature(raw_body, x_line_signature):
        raise HTTPException(status_code=403, detail="Invalid LINE signature")

    body = await request.json()
    events = body.get("events", [])

    logger.info("📩 LINE webhook received")

    # ✅ เช็ก DB แค่ครั้งเดียว
    get_db()

    for event in events:
        if event.get("type") != "message":
            continue
        if event["message"]["type"] != "text":
            continue

        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]
        text = event["message"]["text"]

        user_hash = hash_user(user_id)
        session_id = user_hash

        try:
            await insert_message(
                user_hash=user_hash,
                session_id=session_id,
                role="user",
                content=text
            )

            reply_text = f"คุณพิมพ์ว่า: {text}"

            await insert_message(
                user_hash=user_hash,
                session_id=session_id,
                role="assistant",
                content=reply_text
            )

            await reply_message(
                reply_token=reply_token,
                text=reply_text
            )

        except Exception as e:
            logger.exception("❌ Webhook error")
            raise HTTPException(status_code=500, detail="Webhook processing failed")

    return {"status": "ok"}
