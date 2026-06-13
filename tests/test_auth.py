from fastapi.testclient import TestClient
from unittest import mock
from unittest.mock import patch

from app.main import app
from app.config import settings
from app.routes.auth import USERS

client = TestClient(app)

@patch("app.routes.auth.get_session")
def test_me_success(mock_get_session):
    mock_get_session.return_value = {"username": "testuser"}

    # Set the cookie explicitly for the TestClient
    client.cookies.set(settings.COOKIE_NAME, "valid_sid")

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {"username": "testuser"}
    mock_get_session.assert_called_once_with("valid_sid")

@patch("app.routes.auth.get_session")
def test_me_invalid_session(mock_get_session):
    mock_get_session.return_value = None

    client.cookies.set(settings.COOKIE_NAME, "invalid_sid")

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    mock_get_session.assert_called_once_with("invalid_sid")

@patch("app.routes.auth.get_session")
def test_me_no_cookie(mock_get_session):
    mock_get_session.return_value = None

    # Ensure no cookies are set
    client.cookies.clear()

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    mock_get_session.assert_called_once_with(None)


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
