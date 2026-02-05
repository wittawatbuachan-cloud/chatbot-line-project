from fastapi import APIRouter, Request, Header
from app.message_repo import insert_message
from app.anonymizer import hash_user
from app.line_reply import reply_message
from config.logging_config import get_logger

router = APIRouter()
logger = get_logger("line_webhook", "logs/line_webhook.log")

@router.post("/callback")
async def line_callback(request: Request, x_line_signature: str | None = Header(default=None)):
    logger.info("📩 LINE webhook received")

    body = await request.json()
    events = body.get("events", [])

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

        await reply_message(reply_token=reply_token, text=reply_text)

    return {"status": "ok"}
