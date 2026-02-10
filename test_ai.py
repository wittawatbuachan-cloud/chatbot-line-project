# test_ai.py
import asyncio
from app.ai_service import generate_reply

async def test():
    reply = await generate_reply("I feel empty and exhausted.")
    print(reply)

asyncio.run(test())
