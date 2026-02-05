import httpx
from app.config import settings

async def reply_message(reply_token: str, text: str):
    headers = {
        "Authorization": f"Bearer {settings.line_channel_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {"type": "text", "text": text}
        ]
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=payload
        )
