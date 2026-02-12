# app/metrics_repo.py

from datetime import datetime
from config.db import get_db
from config.logging_config import get_logger

logger = get_logger("metrics_repo", "logs/metrics_repo.log")


async def log_message_metric(
    user_id: str,
    emotion: str,
    risk_level: str,
    latency_ms: float,
    success: bool,
    error_message: str | None = None
):
    db = get_db()

    document = {
        "user_id": user_id,
        "emotion": emotion,
        "risk_level": risk_level,
        "latency_ms": latency_ms,
        "success": success,
        "error_message": error_message,
        "created_at": datetime.utcnow()
    }

    await db.metrics.insert_one(document)
    logger.info(f"Metric logged for user {user_id}")
