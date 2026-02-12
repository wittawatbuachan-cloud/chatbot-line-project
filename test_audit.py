import asyncio
from config.db import connect_db
from app.escalation_manager import create_incident
from app.audit_repo import get_audit_logs


async def test():
    # ✅ เชื่อม MongoDB ก่อน
    await connect_db()

    incident_id = await create_incident(
        user_hash="testhash",
        session_id="testsession",
        emotion="despair",
        risk_level="high",
        keywords=["อยากตาย"],
        content="ฉันอยากตาย"
    )

    print("Incident created:", incident_id)

    logs = await get_audit_logs(limit=5)
    print("\nLatest audit logs:")
    for log in logs:
        print(log)


asyncio.run(test())
