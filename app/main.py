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


@app.get("/")
def root():
    return {"status": "ok"}
