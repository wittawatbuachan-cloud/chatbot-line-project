# app/gemini_client.py
import json
from google import genai
from config.logging_config import get_logger

logger = get_logger("gemini_client", "logs/gemini.log")

client = genai.Client()

SYSTEM_PROMPT = """
You are a professional Thai mental health support assistant.

Your responsibilities:
1. Detect the user's dominant emotion.
2. Assess risk level:
   - low = normal sadness, stress
   - medium = hopelessness, worthlessness
   - high = self-harm or suicide related
3. Respond empathetically and naturally.

IMPORTANT LANGUAGE RULES:
- Always reply in the SAME language as the user.
- If the user writes in Thai, respond in natural Thai.
- Thai responses must sound warm, gentle, and human.
- Avoid direct literal translations from English.
- Use natural Thai conversational tone.
- Do NOT use overly formal bureaucratic language.

CRISIS RULE:
If risk_level is high:
- Respond calmly
- Encourage seeking help
- Provide Thai hotline 1323 and 1669

Return ONLY valid JSON:

{
  "emotion": "...",
  "risk_level": "...",
  "reply": "..."
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
        config={"response_mime_type": "application/json","temperature": 0.7}
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
