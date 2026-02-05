import requests
import os
import json

API_KEY = os.environ["GOOGLE_API_KEY"]

url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

payload = {
    "contents": [
        {
            "parts": [
                {"text": "ตอบกลับมาแบบระบบราชการสั้น ๆ"}
            ]
        }
    ]
}

res = requests.post(url, json=payload)
print("STATUS:", res.status_code)
print(res.text)
