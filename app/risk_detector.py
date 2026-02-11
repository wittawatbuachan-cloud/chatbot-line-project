# app/risk_detector.py

from app.preprocessing import tokenize_text

HIGH_RISK_PHRASES = [
    "อยากตาย",
    "ฆ่าตัวตาย",
    "ไม่อยากมีชีวิตอยู่",
    "จบชีวิต",
    "ตายไปเลย"
]

MEDIUM_RISK_WORDS = [
    "สิ้นหวัง",
    "หมดหวัง",
    "ไม่มีค่า",
    "ไม่ไหวแล้ว",
    "เหนื่อยมาก"
]

def detect_risk_local(text: str):
    text_lower = text.lower()

    # 🔴 ตรวจ phrase ตรง ๆ ก่อน
    for phrase in HIGH_RISK_PHRASES:
        if phrase in text_lower:
            return {
                "risk_level": 3,
                "keywords": [phrase]
            }

    tokens = tokenize_text(text_lower)

    # 🟠 medium
    found_keywords = []
    for word in MEDIUM_RISK_WORDS:
        if word in tokens:
            found_keywords.append(word)

    if found_keywords:
        return {
            "risk_level": 2,
            "keywords": found_keywords
        }

    return {
        "risk_level": 0,
        "keywords": []
    }
