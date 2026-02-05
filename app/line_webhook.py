# app/line_webhook.py
from fastapi import APIRouter, Request, Header, HTTPException
from app.message_repo import insert_message
from app.anonymizer import hash_user
from app.line_reply import reply_message
from config.db import db
from config.logging_config import get_logger

router = APIRouter()
logger = get_logger("line_webhook", "logs/line_webhook.log")

@router.post("/callback")
async def line_callback(
    request: Request,
    x_line_signature: str | None = Header(default=None)
):
    if db is None:
        raise HTTPException(
            status_code=500,
            detail="MongoDB not initialized in webhook"
        )

    body = await request.json()
    events = body.get("events", [])

    logger.info("📩 LINE webhook received")

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
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}
