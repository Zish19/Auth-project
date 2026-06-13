from fastapi.testclient import TestClient
import pytest
from unittest import mock

from app.main import app
from app.routes.auth import USERS

client = TestClient(app)

import pytest
from fastapi.testclient import TestClient
from unittest import mock
from unittest.mock import patch

from app.main import app
from app.routes.auth import USERS
from app.config import settings

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_users():
    USERS.clear()
    yield
    USERS.clear()

def test_register_success():
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "public_key": "testkey"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User registered"}
    assert USERS.get("testuser") == "testkey"

def test_register_duplicate_username():
    # Register first time
    client.post(
        "/auth/register",
        json={"username": "testuser", "public_key": "testkey"}
    )

    # Try to register again
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "public_key": "anotherkey"}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}
    # Verify the key wasn't overwritten
    assert USERS.get("testuser") == "testkey"
def setup_users():
    # Clear the users dict before each test
    USERS.clear()
    yield
    USERS.clear()
from app.config import settings
from fastapi.testclient import TestClient
from unittest import mock

from app.main import app
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

    response = client.post(
        "/auth/login/challenge",
        json={"username": "test_user"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["challenge_id"] == "mock_challenge_id"
    assert data["challenge"] == "mock_challenge_string"
    assert "expires_in" in data
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
