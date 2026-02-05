from google import genai
import os

# สร้าง client (ใช้ API Key จาก env)
client = genai.Client(
    api_key=os.environ["GOOGLE_API_KEY"]
)

# เรียก model ที่รองรับแน่นอน
response = client.models.generate_content(
    model="gemini-1.5-pro-001",
    contents="กรุณาตอบกลับมาในรูปแบบข้อความทางราชการอย่างสุภาพและกระชับ"
)

print(response.text)
