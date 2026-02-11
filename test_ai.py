# test_ai.py
import asyncio
from app.ai_service import generate_reply

async def test():
    reply = await generate_reply(
    user_id="test_user_1",
    user_message="ฉันไม่อยากมีชีวิตอยู่แล้ว"
    )


asyncio.run(test())
