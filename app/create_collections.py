# app/create_collections.py

import asyncio
from config.db import get_db


async def create_indexes():
    db = get_db()

    # metrics indexes
    await db.metrics.create_index("created_at")
    await db.metrics.create_index("risk_level")
    await db.metrics.create_index("success")

    # configs index
    await db.configs.create_index("_id", unique=True)

    print("✅ Collections and indexes created")


if __name__ == "__main__":
    asyncio.run(create_indexes())
