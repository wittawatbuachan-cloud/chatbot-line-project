# app/main.py
from fastapi import FastAPI
from config.db import connect_db, close_db, get_db
from app.line_webhook import router as line_router
from app.admin_router import router as admin_router
from config.logging_config import get_logger

logger = get_logger("main", "logs/main.log")
app = FastAPI()

app.include_router(line_router)
app.include_router(admin_router)   # 👈 สำคัญมาก

@app.on_event("startup")
async def startup():
    logger.info("🚀 FASTAPI STARTUP")
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health/db")
async def health_db():
    try:
        # pydantic settings + connect_db ensure db available
        db = get_db()
        await db.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "detail": str(e)}

# admin: risk summary
@app.get("/admin/risk-summary")
async def risk_summary():
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$risk_level", "count": {"$sum": 1}}},
        {"$sort": {"_id": -1}}
    ]
    rows = await db.messages.aggregate(pipeline).to_list(length=20)
    return {"summary": rows}
