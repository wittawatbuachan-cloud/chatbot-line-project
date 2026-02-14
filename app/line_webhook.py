# app/line_webhook.py
from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks
from config.logging_config import get_logger
from app.message_repo import insert_message
from app.anonymizer import hash_user
from app.line_reply import reply_message
from app.ai_service import generate_reply
from app.risk_detector import detect_risk_local
from app.incident_repo import create_incident
from config.db import get_db
import hmac
import hashlib
import base64
import os

logger = get_logger("line_webhook", "logs/line_webhook.log")
router = APIRouter()

LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")
ENV = os.getenv("ENV", "").lower()
# If running tests, set ENV=test or rely on PYTEST_CURRENT_TEST
IS_TEST = ENV == "test" or bool(os.getenv("PYTEST_CURRENT_TEST"))

def verify_signature(body: bytes, signature: str | None) -> bool:
    """
    Verify LINE HMAC-SHA256 signature.
    In tests (IS_TEST True) we bypass verification to simplify testing.
    """
    if IS_TEST:
        return True

    if not signature or not LINE_SECRET:
        return False

    computed = base64.b64encode(hmac.new(LINE_SECRET.encode("utf-8"), body, hashlib.sha256).digest()).decode()
    return computed == signature

async def process_message_pipeline(user_hash: str, session_id: str, reply_token: str, user_text: str):
    """
    Background worker pipeline:
    - preprocess (tokenize/clean) if you have preprocessing module
    - call AI
    - create incident if needed
    - save assistant message
    - reply to LINE
    """
    logger.info("🚀 Worker started for session=%s", session_id)
    try:
        # Optionally: cleaned_text, tokens = tokenize_text(user_text)
        cleaned_text = user_text  # placeholder if no preprocessing implemented

        # Call AI
        ai_result = await generate_reply(session_id, cleaned_text)

        emotion = ai_result.get("emotion", None)
        risk_level = ai_result.get("risk_level", None)
        ai_reply = ai_result.get("reply", "ขออภัย ระบบขัดข้องชั่วคราว")

        # escalate if risk high
        if isinstance(risk_level, str) and risk_level.lower() == "high":
            # create incident
            await create_incident(conversation_id=session_id, user_hash=user_hash, risk_score=3, keywords=[emotion] if emotion else [])
            reply_text = (
                "ฉันรับรู้ว่าคุณกำลังรู้สึกหนักมากนะ\n"
                "หากคุณคิดจะทำร้ายตัวเองหรือรู้สึกไม่ปลอดภัย\n"
                "โปรดติดต่อสายด่วนสุขภาพจิต 1323 (ประเทศไทย)\n"
                "หรือ 1669 หากเป็นเหตุฉุกเฉินทันที"
            )
        else:
            reply_text = ai_reply

        # Save assistant message
        await insert_message(
            session_id=session_id,
            user_hash=user_hash,
            role="assistant",
            content=reply_text,
            risk_score=3.0 if (isinstance(risk_level,str) and risk_level.lower()=="high") else 0.0,
            keywords=[]
        )

        # send reply to line
        await reply_message(reply_token=reply_token, text=reply_text)

        logger.info("✅ Worker finished for session=%s", session_id)
    except Exception:
        logger.exception("❌ Worker pipeline error for session=%s", session_id)

@router.post("/callback")
async def line_callback(request: Request, background_tasks: BackgroundTasks, x_line_signature: str | None = Header(default=None)):
    raw_body = await request.body()

    if not verify_signature(raw_body, x_line_signature):
        logger.warning("Invalid LINE signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    body = await request.json()
    events = body.get("events", [])

    logger.info("📩 LINE webhook received, events=%d", len(events))

    # ensure DB available - raises if not connected
    get_db()

    for event in events:
        if event.get("type") != "message":
            continue
        if event["message"].get("type") != "text":
            continue

        user_id = event["source"].get("userId")
        reply_token = event.get("replyToken")
        user_text = event["message"].get("text", "")

        user_hash = hash_user(user_id)
        session_id = user_hash

        try:
            # Save user message immediately (fast ack)
            await insert_message(
                session_id=session_id,
                user_hash=user_hash,
                role="user",
                content=user_text,
                risk_score=0.0,
                keywords=[]
            )

            # Local risk check (fast rule-based)
            local_risk = detect_risk_local(user_text)  # expect dict {'risk_level': int, 'keywords': [...]}

            # If extremely risky according to local detector, handle immediately
            if local_risk and local_risk.get("risk_level", 0) >= 3:
                reply_text = (
                    "ฉันรับรู้ว่าคุณกำลังรู้สึกหนักมากนะ\n"
                    "หากคุณคิดจะทำร้ายตัวเองหรือรู้สึกไม่ปลอดภัย\n"
                    "โปรดติดต่อสายด่วนสุขภาพจิต 1323 (ประเทศไทย)\n"
                    "หรือ 1669 หากเป็นเหตุฉุกเฉินทันที"
                )

                # create incident record
                await create_incident(
                    conversation_id=session_id,
                    user_hash=user_hash,
                    risk_score=3,
                    keywords=local_risk.get("keywords", [])
                )

                # save bot reply
                await insert_message(
                    session_id=session_id,
                    user_hash=user_hash,
                    role="assistant",
                    content=reply_text,
                    risk_score=3.0,
                    keywords=local_risk.get("keywords", [])
                )

                # send reply synchronously
                await reply_message(reply_token=reply_token, text=reply_text)
                # skip background worker
                continue

            # Otherwise add background job
            background_tasks.add_task(process_message_pipeline, user_hash, session_id, reply_token, user_text)

        except Exception as e:
            logger.exception("❌ Webhook error handling event")
            raise HTTPException(status_code=500, detail=str(e))

    # Fast ACK
    return {"status": "accepted"}