# app/line_webhook.py
from fastapi import APIRouter, Request, Header, HTTPException
from app.message_repo import insert_message
from app.anonymizer import hash_user
from app.line_reply import reply_message
from app.ai_service import generate_reply
from app.risk_detector import detect_risk_local
from app.preprocessing import tokenize_text
from config.db import get_db
from config.logging_config import get_logger
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

    computed_signature = base64.b64encode(
        hmac.new(LINE_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    ).decode()

    return computed_signature == signature


@router.post("/callback")
async def line_callback(
    request: Request,
    x_line_signature: str | None = Header(default=None)
):

    raw_body = await request.body()

    if not verify_signature(raw_body, x_line_signature):
        raise HTTPException(status_code=403, detail="Invalid LINE signature")

    body = await request.json()
    events = body.get("events", [])

    logger.info("📩 LINE webhook received")

    get_db()

    for event in events:

        if event.get("type") != "message":
            continue
        if event["message"]["type"] != "text":
            continue

        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]
        user_text = event["message"]["text"]

        user_hash = hash_user(user_id)
        session_id = user_hash

        try:
            # ==============================
            # 1️⃣ Preprocess ข้อความ
            # ==============================
            cleaned_text, tokens = tokenize_text(user_text)

            logger.info(f"🧹 Cleaned text: {cleaned_text}")

            # ==============================
            # 2️⃣ Local Risk Detection (Fail-safe)
            # ==============================
            local_risk = detect_risk_local(cleaned_text)

            logger.info(f"🛑 Local risk result: {local_risk}")

            # 🔴 ถ้า Local ตรวจเจอ High → ตอบทันที (ไม่เรียก Gemini)
            if local_risk["risk_level"] >= 3:

                reply_text = (
                    "ฉันรับรู้ว่าคุณกำลังรู้สึกหนักมากนะ\n"
                    "หากคุณคิดจะทำร้ายตัวเองหรือรู้สึกไม่ปลอดภัย\n"
                    "โปรดติดต่อสายด่วนสุขภาพจิต 1323 (ประเทศไทย)\n"
                    "หรือ 1669 หากเป็นเหตุฉุกเฉินทันที"
                )

                # 💾 บันทึก user
                await insert_message(
                    user_hash=user_hash,
                    session_id=session_id,
                    role="user",
                    content=user_text,
                    emotion=None,
                    risk_level="high",
                    source="line"
                )

                # 💾 บันทึก bot
                await insert_message(
                    user_hash=user_hash,
                    session_id=session_id,
                    role="assistant",
                    content=reply_text,
                    emotion=None,
                    risk_level="high",
                    source="system"
                )

                await reply_message(
                    reply_token=reply_token,
                    text=reply_text
                )

                continue  # ข้าม Gemini ไปเลย

            # ==============================
            # 3️⃣ เรียก Gemini Production
            # ==============================
            ai_result = await generate_reply(cleaned_text)

            emotion = ai_result["emotion"]
            risk_level = ai_result["risk_level"]
            ai_reply = ai_result["reply"]

            # 🔴 ถ้า Gemini ประเมิน High
            if risk_level == "high":
                reply_text = (
                    "ฉันรับรู้ว่าคุณกำลังรู้สึกหนักมากนะ\n"
                    "หากคุณคิดจะทำร้ายตัวเองหรือรู้สึกไม่ปลอดภัย\n"
                    "โปรดติดต่อสายด่วนสุขภาพจิต 1323 (ประเทศไทย)\n"
                    "หรือ 1669 หากเป็นเหตุฉุกเฉินทันที"
                )
            else:
                reply_text = ai_reply

            # ==============================
            # 4️⃣ บันทึกข้อความ
            # ==============================

            await insert_message(
                user_hash=user_hash,
                session_id=session_id,
                role="user",
                content=user_text,
                emotion=emotion,
                risk_level=risk_level,
                source="line"
            )

            await insert_message(
                user_hash=user_hash,
                session_id=session_id,
                role="assistant",
                content=reply_text,
                emotion=emotion,
                risk_level=risk_level,
                source="gemini"
            )

            # ==============================
            # 5️⃣ ส่งกลับ LINE
            # ==============================
            await reply_message(
                reply_token=reply_token,
                text=reply_text
            )

        except Exception as e:
            logger.exception("❌ Webhook error")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"status": "ok"}
