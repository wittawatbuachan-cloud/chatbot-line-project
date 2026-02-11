# app/line_reply.py

import httpx
from app.config import settings
from config.logging_config import get_logger

logger = get_logger("line_reply", "logs/line_reply.log")


async def reply_message(*, reply_token: str, text: str):

    if not settings.line_channel_token:
        raise RuntimeError("LINE channel token not configured")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.line_channel_token}"
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=payload
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.exception("❌ LINE API error")
            raise

    logger.info("📤 LINE reply sent successfully")
