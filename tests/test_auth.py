import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.routes.auth import USERS
from app.config import settings

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_users():
    # Clear the users dict before each test
    USERS.clear()
    yield
    USERS.clear()


def test_login_verify_user_not_found():
    # User is not in USERS
    payload = {
        "username": "testuser",
        "challenge_id": "testchallenge_1234",
        "R": "dummy_R",
        "s": "dummy_s"
    }

    response = client.post("/auth/login/verify", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@patch("app.routes.auth.verify_login_attempt")
def test_login_verify_success(mock_verify):
    # Setup user in USERS
    USERS["testuser"] = "test_public_key"

    # Mock the verification to return a session ID
    mock_session_id = "test_session_id_123"
    mock_verify.return_value = mock_session_id

    payload = {
        "username": "testuser",
        "challenge_id": "testchallenge_1234",
        "R": "dummy_R",
        "s": "dummy_s"
    }

    response = client.post("/auth/login/verify", json=payload)

    # Check that verify_login_attempt was called with the correct parameters
    mock_verify.assert_called_once_with(
        username="testuser",
        user_public_key="test_public_key",
        challenge_id="testchallenge_1234",
        R="dummy_R",
        s="dummy_s"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Login success"

    # Check cookies
    cookies = response.cookies
    assert settings.COOKIE_NAME in cookies
    assert cookies[settings.COOKIE_NAME] == mock_session_id
