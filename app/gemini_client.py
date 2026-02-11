# app/gemini_client.py
import json
from google import genai
from config.logging_config import get_logger

logger = get_logger("gemini_client", "logs/gemini.log")

client = genai.Client()

SYSTEM_PROMPT = """
You are a mental health support AI.

Tasks:
1. Detect dominant emotion.
2. Assess risk level:
   - low
   - medium
   - high
3. Respond empathetically.

Return ONLY valid JSON:

{
  "emotion": "sadness",
  "risk_level": "low",
  "reply": "empathetic message"
}
"""


async def generate_empathetic_response(user_message: str):

    full_prompt = f"""
{SYSTEM_PROMPT}

User message:
{user_message}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt,
        config={"response_mime_type": "application/json"}
    )

    text = response.text.strip()
    logger.info(f"RAW GEMINI: {text}")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "emotion": "unknown",
            "risk_level": "unknown",
            "reply": text
        }
