# tests/test_integration.py
import pytest
from httpx import AsyncClient
from app.main import app
from unittest.mock import AsyncMock, patch
import time


@pytest.mark.asyncio
async def test_full_line_flow():
    with patch("app.line_webhook.insert_message", new_callable=AsyncMock):

        async with AsyncClient(app=app, base_url="http://test") as ac:
            start = time.time()

            response = await ac.post(
                "/callback",
                json={
                    "events": [
                        {
                            "type": "message",
                            "replyToken": "test",
                            "source": {"userId": "U123"},
                            "message": {"type": "text", "text": "สวัสดี"}
                        }
                    ]
                }
            )

            elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 3
