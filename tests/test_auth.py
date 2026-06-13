import pytest
from fastapi.testclient import TestClient
from unittest import mock
from unittest.mock import patch

from app.main import app
from app.config import settings
from app.routes.auth import USERS

client = TestClient(app)

def test_login_challenge_user_not_found():
    response = client.post(
        "/auth/login/challenge",
        json={"username": "non_existent_user"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

@mock.patch("app.routes.auth.create_challenge")
def test_login_challenge_success(mock_create_challenge):
    mock_create_challenge.return_value = ("mock_challenge_id", "mock_challenge_string")

    # Add a user to the global USERS dict for the duration of this test
    USERS["test_user"] = "mock_public_key"

    try:
        response = client.post(
            "/auth/login/challenge",
            json={"username": "test_user"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["challenge_id"] == "mock_challenge_id"
        assert data["challenge"] == "mock_challenge_string"
        assert "expires_in" in data
    finally:
        # Cleanup
        if "test_user" in USERS:
            del USERS["test_user"]

@patch("app.routes.auth.destroy_session")
def test_logout_with_cookie(mock_destroy_session):
    # Set up the cookie in the TestClient
    client.cookies.set(settings.COOKIE_NAME, "test_sid_123")

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}

    # Verify destroy_session was called
    mock_destroy_session.assert_called_once_with("test_sid_123")

    # Verify cookie was deleted
    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert settings.COOKIE_NAME in set_cookie
    assert 'Max-Age=0' in set_cookie or 'expires=' in set_cookie.lower()

@patch("app.routes.auth.destroy_session")
def test_logout_without_cookie(mock_destroy_session):
    # Ensure no cookies are set
    client.cookies.clear()

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}

    # Verify destroy_session was called with None
    mock_destroy_session.assert_called_once_with(None)
