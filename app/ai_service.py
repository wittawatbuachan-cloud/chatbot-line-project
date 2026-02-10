# app/ai_service.py

from typing import Literal

MODE: Literal["mock", "gemini"] = "mock"  # เปลี่ยนทีหลังได้

def generate_reply(user_message: str) -> str:
    if MODE == "mock":
        return (
            "I hear you. It sounds like you're dealing with something difficult. "
            "It's okay to feel this way, and you're not alone."
        )

    # --- Gemini (STEP ถัดไป) ---
    # from app.gemini_client import generate_empathetic_response
    # return generate_empathetic_response(user_message)
