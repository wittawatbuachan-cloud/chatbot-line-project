# app/ai_service.py

from typing import Optional, Dict, Any, List
from config.logging_config import get_logger
from app.prompt_manager import build_prompt
from app.configs_repo import get_system_config
from app.gemini_client import generate_empathetic_response
from config.db import get_db

logger = get_logger("ai_service", "logs/ai_service.log")


async def _get_recent_messages(session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch the most recent messages for a session from the messages collection.
    Returns a list ordered oldest -> newest.
    """
    db = get_db()
    cursor = db.messages.find({"session_id": session_id}).sort("trigger_ts", -1).limit(limit)
    msgs = []
    async for doc in cursor:
        msgs.append({
            "role": doc.get("role"),
            "content": doc.get("content")
        })
    msgs.reverse()
    return msgs


async def generate_reply(user_hash: str, session_id: str, user_text: str) -> Dict[str, Any]:
    """
    High-level AI service:
      - load system config/prompts
      - gather recent context
      - build prompt via prompt_manager
      - call gemini_client and return normalized result

    Return dict: { "emotion": str, "risk_level": str|int, "reply": str }
    """
    try:
        # 1) load prompt config (auto-seeds if missing)
        config_prompts = await get_system_config()

        # 2) gather recent context
        recent_context = await _get_recent_messages(session_id, limit=5)

        # 3) (optional) user_profile - placeholder, extend if you store profiles
        user_profile: Optional[Dict[str, Any]] = None

        # 4) build prompt
        prompt_text = build_prompt(
            cleaned_text=user_text,
            recent_context=recent_context,
            user_profile=user_profile,
            config_prompts=config_prompts or {}
        )

        logger.debug("Built prompt (len=%d) for session=%s", len(prompt_text), session_id)

        # 5) call Gemini wrapper
        result = await generate_empathetic_response(prompt_text)

        # 6) normalize/validate result shape
        if not isinstance(result, dict):
            logger.warning("AI result not dict; converting to fallback")
            return {"emotion": "unknown", "risk_level": "unknown", "reply": str(result)}

        # ensure keys exist
        emotion = result.get("emotion", "unknown")
        risk_level = result.get("risk_level", "unknown")
        reply = result.get("reply", "")

        return {"emotion": emotion, "risk_level": risk_level, "reply": reply}

    except Exception as e:
        logger.exception("generate_reply failed")
        return {
            "emotion": "error",
            "risk_level": "unknown",
            "reply": "ขออภัย ระบบขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้ง"
        }