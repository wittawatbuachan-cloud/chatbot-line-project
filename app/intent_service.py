# app/intent_service.py

from app.risk_detector import detect_risk_local

INTENT_KEYWORDS = {
    "greeting": ["สวัสดี", "hello", "hi"],
    "help": ["ช่วย", "help"],
    "emotional_support": ["เศร้า", "หมดหวัง", "เหนื่อย"]
}


def detect_intent(text: str):
    for intent, keywords in INTENT_KEYWORDS.items():
        for k in keywords:
            if k in text:
                return intent
    return "unknown"


def hybrid_analysis(text: str, gemini_result: dict):
    """
    Combine local rule + Gemini semantic output
    Return standardized output for pipeline
    """

    local = detect_risk_local(text)

    risk_score = 0.0

    if gemini_result["risk_level"] == "high":
        risk_score = 0.9
    elif gemini_result["risk_level"] == "medium":
        risk_score = 0.6
    elif gemini_result["risk_level"] == "low":
        risk_score = 0.3

    # override if local rule detected critical keyword
    if local["risk_level"] >= 3:
        risk_score = 1.0

    return {
        "intent": detect_intent(text),
        "emotion": gemini_result.get("emotion", "unknown"),
        "risk_score": risk_score,
        "risk_level": gemini_result.get("risk_level", "low")
    }
