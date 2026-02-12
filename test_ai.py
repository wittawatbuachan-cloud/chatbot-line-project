import pytest
from unittest.mock import patch, MagicMock
from app.gemini_client import generate_empathetic_response

@pytest.mark.asyncio
async def test_generate_mock():

    mock_response = MagicMock()
    mock_response.text = """
    {
        "emotion": "sadness",
        "risk_level": "low",
        "reply": "เข้าใจความรู้สึกของคุณนะ"
    }
    """

    with patch("app.gemini_client.client.models.generate_content", return_value=mock_response):

        result = await generate_empathetic_response("ฉันเศร้า")

        assert result["emotion"] == "sadness"
        assert result["risk_level"] == "low"
