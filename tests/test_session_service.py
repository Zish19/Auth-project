import json
import pytest
from unittest.mock import patch

from app.services.session_service import create_session, get_session
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


def test_get_session_empty_sid():
    """Test getting session with empty sid."""
    assert get_session("") is None
    assert get_session(None) is None


@patch("app.services.session_service.r.get")
@patch("app.services.session_service.logger.exception")
def test_get_session_redis_failure(mock_logger_exception, mock_get):
    """Test getting session when Redis fails."""
    mock_get.side_effect = Exception("Redis connection error")

    assert get_session("test_sid") is None
    mock_logger_exception.assert_called_once_with("auth.session.fetch_failed")


@patch("app.services.session_service.r.get")
def test_get_session_not_found(mock_get):
    """Test getting session when session is not found in Redis."""
    mock_get.return_value = None
    assert get_session("test_sid") is None


@patch("app.services.session_service.r.get")
@patch("app.services.session_service.logger.warning")
def test_get_session_invalid_json(mock_logger_warning, mock_get):
    """Test getting session when Redis returns invalid JSON."""
    mock_get.return_value = "invalid json payload"

    assert get_session("test_sid") is None
    mock_logger_warning.assert_called_once_with("auth.session.invalid_payload")


@patch("app.services.session_service.r.get")
@patch("app.services.session_service.logger.warning")
def test_get_session_invalid_shape_not_dict(mock_logger_warning, mock_get):
    """Test getting session when the JSON payload is not a dictionary."""
    mock_get.return_value = json.dumps(["a", "list"])

    assert get_session("test_sid") is None
    mock_logger_warning.assert_called_once_with("auth.session.invalid_shape")


@patch("app.services.session_service.r.get")
@patch("app.services.session_service.logger.warning")
def test_get_session_invalid_shape_no_username(mock_logger_warning, mock_get):
    """Test getting session when the JSON dict is missing the 'username' key."""
    mock_get.return_value = json.dumps({"other_key": "value"})

    assert get_session("test_sid") is None
    mock_logger_warning.assert_called_once_with("auth.session.invalid_shape")


@patch("app.services.session_service.r.get")
def test_get_session_success(mock_get):
    """Test successful session retrieval."""
    expected_session = {"username": "test_user"}
    mock_get.return_value = json.dumps(expected_session)

    session = get_session("test_sid")
    assert session == expected_session
    mock_get.assert_called_once_with("session:test_sid")
