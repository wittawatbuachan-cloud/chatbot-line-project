# tests/test_gemini_client.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_gemini_mock():
    with patch("app.gemini_client.generate_empathetic_response", new_callable=AsyncMock) as mock:
        mock.return_value = "Mocked reply"
        result = await mock()
        assert result == "Mocked reply"
