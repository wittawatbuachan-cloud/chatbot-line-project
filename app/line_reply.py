# app/line_reply.py
import httpx
from app.config import settings
from config.logging_config import get_logger
from app.ai_service import generate_reply

logger = get_logger("line_reply", "logs/line_reply.log")

async def reply_message(*, reply_token: str, user_text: str):
    ai_text = generate_reply(user_text)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.line_channel_token}"
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {"type": "text", "text": ai_text}
        ]
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=payload
        )
        try:
            r.raise_for_status()
        except Exception as e:
            logger.exception("Failed to send LINE reply")
            raise
    logger.info("📤 LINE reply sent")
