import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.message_repo import insert_message


@pytest.mark.asyncio
async def test_insert_message_success():

    # Mock inserted_id
    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = "mocked_id"

    # Mock collection
    mock_collection = MagicMock()
    mock_collection.insert_one = AsyncMock(return_value=mock_insert_result)

    # Mock db
    mock_db = MagicMock()
    mock_db.messages = mock_collection

    # Patch get_db to return mock_db
    with patch("app.message_repo.get_db", return_value=mock_db):

        result = await insert_message(
            session_id="S1",
            user_hash="U_HASH",
            role="user",
            content="hello",
            risk_score=0.5,
            keywords=["test"]
        )

        # ตรวจว่า insert_one ถูกเรียก
        mock_collection.insert_one.assert_called_once()

        # ตรวจว่า return id ถูกต้อง
        assert result == "mocked_id"
