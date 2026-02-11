# app/safety_filter.py

FORBIDDEN_MEDICAL_WORDS = [
    "ยา", "prescribe", "diagnosis",
    "antidepressant", "SSRI"
]


def contains_medical_claim(text: str):
    for word in FORBIDDEN_MEDICAL_WORDS:
        if word.lower() in text.lower():
            return True
    return False


def apply_post_llm_safety(reply: str, risk_level: str):
    if contains_medical_claim(reply):
        return (
            "ฉันไม่สามารถให้คำแนะนำทางการแพทย์ได้ "
            "หากคุณกังวลเรื่องสุขภาพ โปรดปรึกษาผู้เชี่ยวชาญโดยตรง"
        )

    if risk_level == "high":
        return (
            "หากคุณรู้สึกไม่ปลอดภัย โปรดติดต่อสายด่วนสุขภาพจิต 1323 "
            "หรือ 1669 หากเป็นเหตุฉุกเฉินทันที"
        )

    return reply
