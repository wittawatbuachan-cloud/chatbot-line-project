# app/risk_detector.py
# Rule-based risk detector (simple and auditable)
from typing import Dict, List

RISK_KEYWORDS = {
    3: ["อยากตาย", "ฆ่าตัวตาย", "ไม่อยากมีชีวิตอยู่", "จบชีวิต", "จะฆ่า", "คิดจะตาย"],
    2: ["สิ้นหวัง", "ไม่เหลืออะไร", "หมดความหวัง", "ไม่ไหวแล้ว", "ทนไม่ไหว"],
    1: ["ท้อแท้", "เศร้า", "เครียด", "เหนื่อยใจ", "แย่มาก"]
}

def detect_risk(text: str) -> Dict[str, object]:
    if not text:
        return {"risk_level": 0, "keywords": []}

    t = text.lower()
    found: List[str] = []
    for level in (3, 2, 1):
        hits = [kw for kw in RISK_KEYWORDS[level] if kw in t]
        if hits:
            # return highest matched level
            return {"risk_level": level, "keywords": hits}
    return {"risk_level": 0, "keywords": []}
