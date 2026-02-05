# app/anonymizer.py
import hashlib

def hash_user(user_id: str, salt: str = "chatbot_salt") -> str:
    raw = f"{user_id}{salt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
