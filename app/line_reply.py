import httpx
from config.logging_config import get_logger
from app.config import settings

logger = get_logger("line_reply", "logs/line_reply.log")

async def reply_message(reply_token: str, text: str):
    """
    Send reply to LINE Messaging API.
    """

    token = settings.LINE_CHANNEL_TOKEN

    if not token:
        logger.error("❌ LINE channel token not configured")
        raise RuntimeError("LINE channel token not configured")

    logger.info("📤 Preparing LINE reply (token loaded: %s...)", token[:10])

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

    logger.debug("LINE payload: %s", payload)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                "https://api.line.me/v2/bot/message/reply",
                headers=headers,
                json=payload
            )

            logger.info("📡 LINE response status: %s", response.status_code)

            if response.status_code != 200:
                logger.error("❌ LINE error body: %s", response.text)

            response.raise_for_status()

        except Exception:
            logger.exception("❌ Failed to send LINE reply")
            raise

    logger.info("✅ LINE reply sent successfully")
    return True