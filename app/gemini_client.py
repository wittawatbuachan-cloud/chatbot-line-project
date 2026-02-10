# app/gemini_client.py
import os
import time
from google import genai
from google.genai import errors
from config.logging_config import get_logger

logger = get_logger("gemini_client", "logs/gemini.log")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """
คุณคือผู้ช่วย AI ที่มีความเข้าใจทางอารมณ์ (Empathetic AI)

หน้าที่หลักของคุณคือ
- เข้าใจความรู้สึกของผู้ใช้
- แสดงความเห็นอกเห็นใจ
- ตอบด้วยถ้อยคำสุภาพ อ่อนโยน และเป็นมิตร

แนวทางการตอบ:
- กล่าวถึงอารมณ์ของผู้ใช้โดยตรง
- ไม่ตัดสิน ไม่ตำหนิ
- ไม่ให้คำแนะนำรุนแรงหรือเร่งรีบ
- ใช้ภาษาที่เป็นธรรมชาติ เหมือนมนุษย์พูดกับมนุษย์
- หากเหมาะสม ให้ถามคำถามปลายเปิดอย่างนุ่มนวลเพียง 1 คำถาม

ข้อจำกัด:
- คุณไม่ใช่แพทย์หรือนักจิตวิทยา
- ห้ามวินิจฉัยหรือให้คำแนะนำทางการแพทย์
- เน้นการรับฟังและสนับสนุนทางอารมณ์เป็นหลัก

**ตอบกลับเป็นภาษาไทยเท่านั้น**
"""

async def generate_empathetic_response(user_message: str) -> str:
    full_prompt = f"""
{SYSTEM_PROMPT}

ผู้ใช้พิมพ์ข้อความดังนี้ (ภาษาไทย):
{user_message}

กรุณาตอบกลับด้วยภาษาไทยอย่างสุภาพและแสดงความเข้าใจทางอารมณ์:
"""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            return response.text

        except errors.ClientError as e:
            error_code = None

            if hasattr(e, "response") and e.response is not None:
                error_code = e.response.status_code

            if error_code == 429:
                wait = 10 * (attempt + 1)
                logger.warning(f"Gemini quota exhausted. Retry in {wait}s")
                time.sleep(wait)
            else:
                logger.exception("Gemini API error")
                raise


    return "I'm here with you. The system is a bit busy right now, but I'm listening."
