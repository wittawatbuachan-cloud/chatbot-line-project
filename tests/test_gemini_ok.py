from google import genai
import os

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

response = client.models.generate_content(
    model="models/gemini-1.5-pro",
    contents="ตอบกลับมาแบบระบบราชการสั้น ๆ"
)

print(response.text)
