# app/main.py
from fastapi import FastAPI
from config.db import connect_db, close_db
from app.line_webhook import router as line_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("🚀 FASTAPI STARTUP")
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    print("🛑 FASTAPI SHUTDOWN")
    await close_db()

app.include_router(line_router)
