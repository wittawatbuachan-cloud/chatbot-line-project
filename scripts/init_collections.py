import asyncio
from config.db import connect_db, close_db

from app.schemas.conversations_schema import create_conversations_collection
from app.schemas.incidents_schema import create_incidents_collection
from app.schemas.configs_schema import create_configs_collection
from app.schemas.audit_logs_schema import create_audit_logs_collection



async def main():
    await connect_db()

    await create_conversations_collection()
    await create_incidents_collection()
    await create_configs_collection()
    await create_audit_logs_collection()
    

    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
