from fastapi import FastAPI
from config.db import connect_db, close_db

app = FastAPI()


@app.on_event("startup")
async def startup():
    print("🚀 FASTAPI STARTUP")
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/health/db")
async def health_db():
    try:
        await db.command("ping")
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(e)
        }