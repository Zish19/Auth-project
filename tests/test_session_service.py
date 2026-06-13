import json
import pytest
from unittest.mock import patch

from app.services.session_service import create_session
from app.config import settings


@patch("app.services.session_service.r.setex")
@patch("app.services.session_service.secrets.token_urlsafe")
def test_create_session_success(mock_token_urlsafe, mock_setex):
    """Test successful session creation."""
    mock_sid = "mocked_secure_token_123"
    mock_token_urlsafe.return_value = mock_sid

    username = "test_user"

    sid = create_session(username)

    # Check returned value is the generated token
    assert sid == mock_sid

    # Check token_urlsafe was called correctly
    mock_token_urlsafe.assert_called_once_with(32)

    # Check if redis setex was called with correct arguments
    key = f"session:{mock_sid}"
    expected_payload = json.dumps({"username": username})

    mock_setex.assert_called_once_with(
        key,
        settings.SESSION_TTL_SECONDS,
        expected_payload
    )


@patch("app.services.session_service.r.setex")
def test_create_session_redis_failure(mock_setex):
    """Test session creation when Redis fails."""
    mock_setex.side_effect = Exception("Redis connection error")

    username = "error_user"

    with pytest.raises(Exception, match="Redis connection error"):
        create_session(username)
