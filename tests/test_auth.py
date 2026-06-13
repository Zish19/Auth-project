from fastapi.testclient import TestClient
import pytest
from unittest import mock

from app.main import app
from app.routes.auth import USERS

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
