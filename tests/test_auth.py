from fastapi.testclient import TestClient
from unittest import mock

from app.main import app
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
