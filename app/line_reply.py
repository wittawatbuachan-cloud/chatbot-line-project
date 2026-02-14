# app/line_reply.py
import httpx
import asyncio
from config.logging_config import get_logger
from app.config import settings  # adjust import path if your settings live elsewhere

logger = get_logger("line_reply", "logs/line_reply.log")

async def reply_message(reply_token: str, text: str):
    """
    Send reply to LINE Messaging API.
    Expects settings.line_channel_token to be set (LINE channel access token).
    """
    token = getattr(settings, "line_channel_token", None)
    if not token:
        logger.error("LINE channel token not configured (settings.line_channel_token)")
        raise RuntimeError("LINE channel token not configured")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {"type": "text", "text": text}
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
        except Exception:
            logger.exception("Failed to send LINE reply")
            raise

    logger.info("📤 LINE reply sent")
    return True