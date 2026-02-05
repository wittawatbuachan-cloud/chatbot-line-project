from google import genai
import os

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="ทดสอบระบบ"
)

print(response.text)

