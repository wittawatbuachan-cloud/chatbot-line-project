import asyncio
from config.db import db

async def test():
    await db.command("ping")
    print("✅ MongoDB connected")

asyncio.run(test())
