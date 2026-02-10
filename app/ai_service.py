# app/ai_service.py
from typing import Literal
from app.gemini_client import generate_empathetic_response

MODE: Literal["mock", "gemini"] = "gemini"

async def generate_reply(user_message: str) -> str:
    if MODE == "mock":
        return (
            "I hear you. It sounds like you're dealing with something difficult. "
            "You're not alone."
        )

    return await generate_empathetic_response(user_message)
