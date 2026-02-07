# app/line_reply.py
import httpx
from app.config import settings

async def reply_message(*, reply_token: str, text: str):
    if not settings.line_channel_token:
        raise RuntimeError("LINE_CHANNEL_TOKEN not configured")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.line_channel_token}",
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {"type": "text", "text": text}
        ]
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=payload
        )
        r.raise_for_status()
