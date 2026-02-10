# app/ai_service.py
from typing import Literal
from app.gemini_client import generate_empathetic_response

MODE: Literal["mock", "gemini"] = "gemini"

async def generate_reply(user_message: str) -> str:
    if MODE == "mock":
        return (
            "ฉันรับรู้ถึงความรู้สึกของคุณนะ "
            "แม้ตอนนี้จะเหนื่อยหรือว่างเปล่า คุณไม่ได้อยู่คนเดียว"
        )

    try:
        return await generate_empathetic_response(user_message)
    except Exception:
        return (
            "ฉันอยู่ตรงนี้นะ แม้ระบบจะช้าลงเล็กน้อย "
            "แต่ความรู้สึกของคุณสำคัญเสมอ"
        )

