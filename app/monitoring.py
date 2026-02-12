# app/monitoring.py

import time
from app.metrics_repo import log_message_metric


class MonitoringContext:

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    async def stop(
        self,
        emotion: str,
        risk_level: str,
        success: bool,
        error_message: str | None = None
    ):
        latency_ms = (time.time() - self.start_time) * 1000

        await log_message_metric(
            user_id=self.user_id,
            emotion=emotion,
            risk_level=risk_level,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message
        )
