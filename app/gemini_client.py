# app/gemini_client.py
import os
import time
from google import genai
from google.genai import errors
from config.logging_config import get_logger

logger = get_logger("gemini_client", "logs/gemini.log")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """
You are an empathetic conversational AI trained to support users emotionally.

Your role is to understand the user's feelings, validate their emotions,
and respond with warmth, kindness, and emotional intelligence.

Guidelines:
- Acknowledge emotions explicitly
- Normalize feelings
- Avoid judgment
- Avoid harsh advice
- Offer emotional support first

You are not a therapist.
Do not diagnose.
"""

async def generate_empathetic_response(user_message: str) -> str:
    full_prompt = f"""
{SYSTEM_PROMPT}

User message:
{user_message}

Empathetic response:
"""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            return response.text

        except errors.ClientError as e:
            if e.status_code == 429:
                wait = 10 * (attempt + 1)
                logger.warning(f"Gemini rate limited. Retry in {wait}s")
                time.sleep(wait)
            else:
                logger.exception("Gemini API error")
                raise

    return "I'm here with you. The system is a bit busy right now, but I'm listening."
