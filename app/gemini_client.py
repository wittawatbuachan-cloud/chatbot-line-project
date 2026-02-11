# app/gemini_client.py
import json
from google import genai
from google.genai import errors
from config.logging_config import get_logger

logger = get_logger("gemini_client", "logs/gemini.log")

client = genai.Client()

SYSTEM_PROMPT = """
You are a mental health support AI.

Your job:
1. Detect user's dominant emotion.
2. Assess risk level:
   - low = normal sadness, stress
   - medium = hopelessness, worthlessness
   - high = self-harm or suicide related
3. Respond empathetically and supportively.

IMPORTANT:
Return ONLY valid JSON format like this:

{
  "emotion": "sadness",
  "risk_level": "low",
  "reply": "empathetic response here"
}

No extra text.
"""


async def generate_empathetic_response(user_message: str):

    full_prompt = f"""
{SYSTEM_PROMPT}

User message:
{user_message}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        text = response.text.strip()
        logger.info(f"RAW GEMINI: {text}")

        result = json.loads(text)
        return result

    except json.JSONDecodeError:
        logger.warning("Gemini did not return valid JSON")

        return {
            "emotion": "unknown",
            "risk_level": "unknown",
            "reply": text if 'text' in locals() else "I'm here with you."
        }

    except errors.ClientError as e:
        logger.error(f"Gemini API error: {e}")

        return {
            "emotion": "system_error",
            "risk_level": "unknown",
            "reply": "The system is temporarily busy. I'm still here with you."
        }
