# app/line_webhook.py
from fastapi import APIRouter, Request, Header, HTTPException
from app.message_repo import insert_message
from app.anonymizer import hash_user
from app.line_reply import reply_message
from config.db import get_db
from config.logging_config import get_logger
from app.risk_detector import detect_risk
import hmac
import hashlib
import base64
import os

LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")
router = APIRouter()
logger = get_logger("line_webhook", "logs/line_webhook.log")

def verify_signature(body: bytes, signature: str | None):
    if not signature or not LINE_SECRET:
        return False
    sig = base64.b64encode(hmac.new(LINE_SECRET.encode("utf-8"), body, hashlib.sha256).digest()).decode()
    return sig == signature

@router.post("/callback")
async def line_callback(request: Request, x_line_signature: str | None = Header(default=None)):
    raw_body = await request.body()

    if not verify_signature(raw_body, x_line_signature):
        raise HTTPException(status_code=403, detail="Invalid LINE signature")

    body = await request.json()
    events = body.get("events", [])

    logger.info("📩 LINE webhook received")

    # ensure DB available
    get_db()

    for event in events:
        if event.get("type") != "message":
            continue
        if event["message"]["type"] != "text":
            continue

        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]
        text = event["message"]["text"]

        user_hash = hash_user(user_id)
        session_id = user_hash

        try:
            # detect risk
            risk = detect_risk(text)
            # insert user message with risk fields
            await insert_message(
                user_hash=user_hash,
                session_id=session_id,
                role="user",
                content=text,
                risk_level=risk["risk_level"],
                risk_keywords=risk["keywords"],
                source="line"
            )

            # compose reply depending on risk level
            if risk["risk_level"] >= 3:
                reply_text = (
                    "ฉันรับรู้ว่าคุณกำลังรู้สึกหนักมากนะ หากคุณคิดจะทำร้ายตัวเอง "
                    "หรือรู้สึกไม่ปลอดภัย กรุณาติดต่อสายด่วนช่วยเหลือหรือผู้ที่ไว้ใจได้ทันที "
                    "สายด่วนสุขภาพจิต 1323 (ในประเทศไทย) หรือหากสถานการณ์ฉุกเฉินโปรดติดต่อ 1669 ครับ/ค่ะ"
                )
            elif risk["risk_level"] == 2:
                reply_text = (
                    "ฉันได้ยินว่าคุณกำลังสิ้นหวังอยู่ ลองพูดคุยกับคนใกล้ชิดหรือผู้เชี่ยวชาญนะ "
                    "ถ้าต้องการ ฉันจะช่วยส่งข้อมูลแหล่งช่วยเหลือให้ได้"
                )
            elif risk["risk_level"] == 1:
                reply_text = "ขอโทษที่คุณรู้สึกแบบนั้นนะ ถ้าพร้อมคุยต่อ ฉันอยู่ตรงนี้นะ"
            else:
                reply_text = f"คุณพิมพ์ว่า: {text}"

            # save assistant reply
            await insert_message(
                user_hash=user_hash,
                session_id=session_id,
                role="assistant",
                content=reply_text,
                risk_level=0,
                source="system"
            )

            # send reply back to LINE
            await reply_message(reply_token=reply_token, text=reply_text)

        except Exception as e:
            logger.exception("❌ Webhook error")
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}
