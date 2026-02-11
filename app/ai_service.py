# app/ai_service.py
from app.gemini_client import generate_empathetic_response


async def generate_reply(user_message: str):
    result = await generate_empathetic_response(user_message)
    return result
