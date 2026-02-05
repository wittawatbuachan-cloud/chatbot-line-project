import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-pro")

response = model.generate_content(
    "กรุณาตอบกลับในรูปแบบข้อความทางราชการอย่างสุภาพและกระชับ"
)

print(response.text)
ก