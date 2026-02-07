from fastapi import FastAPI
import config.db as database
from app.line_webhook import router as line_router

app = FastAPI()

app.include_router(line_router)

@app.on_event("startup")
async def startup():
    await database.connect_db()

@app.on_event("shutdown")
async def shutdown():
    await database.close_db()

@app.get("/health/db")
async def health_db():
    try:
        await database.db.command("ping")
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
