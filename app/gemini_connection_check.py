from google import genai
import os
import logging

# ตั้งค่า logging (Render จะดึง stdout ไปแสดง)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_gemini_connection():
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")

        if not api_key:
            logger.error("❌ GOOGLE_API_KEY not found in environment variables")
            return False

        # สร้าง client (ยังไม่เรียก model)
        client = genai.Client(api_key=api_key)

        # แค่ยืนยันว่า client ถูกสร้างได้
        logger.info("✅ Gemini Client initialized successfully")
        logger.info("ℹ️ API key loaded and SDK ready (model not called)")

        return True

    except Exception as e:
        logger.error("❌ Failed to initialize Gemini Client")
        logger.exception(e)
        return False


if __name__ == "__main__":
    logger.info("🔌 Starting Gemini connection check...")
    check_gemini_connection()
    logger.info("🏁 Gemini connection check finished")
